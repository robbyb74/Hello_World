import logging
import asyncio
from typing import List, Dict

import aiohttp
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class InstallPayload(BaseModel):
    mode: str
    challenge: str
    verify_token: str

    @classmethod
    def of(cls, payload: Dict[str, any]):
        return InstallPayload(
            mode=payload['hub.mode'],
            challenge=payload['hub.challenge'],
            verify_token=payload['hub.verify_token']
        )


class Lead(BaseModel):
    leadgen_id: str
    page_id: str
    form_id: str

    @classmethod
    def of(_cls, payload: Dict[str, any]):
        """https://developers.facebook.com/docs/marketing-api/guides/lead-ads/retrieving/#webhook-response"""
        return [
            Lead(**lead['value'])
            for entry in payload.get('entry', [])
            for lead in entry.get('changes', [])
            if lead['field'] == 'leadgen'
        ]


class FormSubmission(BaseModel):
    page: str
    field_data: Dict[str, any]



class FacebookClient(object):
    access_token: str
    verify_token: str

    def __init__(self, access_token: str, verify_token: str):
        self.access_token = access_token
        self.verify_token = verify_token

    def verify(self, payload: InstallPayload):
        if self.verify_token != payload.verify_token:
            raise ValueError('Invalid verify token')

    @property
    def credentials(self):
        return {
            'params': {
                'access_token': self.access_token
            }
        }

    async def retrieve_page(self, session, page_id: str):
        """https://developers.facebook.com/docs/graph-api/reference/page/

        {
          "id": "897778120337543",
          "name": "S23 Portal"
        }
        """
        url = f'https://graph.facebook.com/v8.0/{page_id}'
        params = self.credentials['params']
        params['fields'] = 'id,name'
        async with session.get(url, params=params) as resp:
            return await resp.json()

    async def retrieve_form(self, session, lead_id: str):
        """https://developers.facebook.com/docs/graph-api/reference/page/

        {
          "created_time": "2015-02-28T08:49:14+0000",
          "id": "<LEAD_ID>",
          "ad_id": "<AD_ID>",
          "form_id": "<FORM_ID>",
          "field_data": [{
            "name": "car_make",
            "values": [
               "Honda"
            ]
          }
        }
        """
        url = f'https://graph.facebook.com/v8.0/{lead_id}'
        async with session.get(url, **self.credentials) as resp:
            return await resp.json()

    async def retrieve_form_submissions(self, leads: List[Lead]):
        async with aiohttp.ClientSession() as session:
            """https://developers.facebook.com/docs/marketing-api/guides/lead-ads/retrieving/#reading-store-locator-question-value"""
            page_mapping = await asyncio.gather(*[
                self.retrieve_page(session, lead.page_id)
                for lead in leads
            ])
            page_mapping = {page['id']: page['name']
                            for page in page_mapping} # page_id -> page_name
            page_mapping = {lead.form_id: page_mapping[lead.page_id]
                            for lead in leads} # form_id -> page_name

            form_list = await asyncio.gather(*[
                self.retrieve_form(session, lead.leadgen_id)
                for lead in leads
            ])

            form_submissions = [FormSubmission(
                page=page_mapping[form['form_id']],
                field_data=form['field_data']
            ) for form in form_list]

            return form_submissions
