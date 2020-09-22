import logging
from typing import Dict

import aiohttp
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class FormSubmission(BaseModel):
    company_id: str
    referrer: str
    referring_url: str
    landing_page_url: str
    form_url: str
    form_data: Dict[str, str]


class CallRailClient(object):
    account_id: str
    api_key: str

    def __init__(self, account_id: str, api_key: str):
        self.account_id = account_id
        self.api_key = api_key

    @property
    def credentials(self):
        return {
            'headers': {
                'Authorization': f'Token token={self.api_key}'
            }
        }

    async def create_form_submission(self, form: FormSubmission):
        url = f'https://api.callrail.com/v3/a/{self.account_id}/form_submissions.json'
        json = {
            "form_submission": form.dict()
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json, **self.credentials) as resp:
                data = await resp.json()
                if resp.status >= 400:
                    raise RuntimeError(data)
                return data
