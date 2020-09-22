import logging
import asyncio

from uvicorn import run
from pydantic import BaseSettings
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse

from leadspipe.facebook import (
    FacebookClient,
    LeadPayload, InstallPayload,
    Lead
)
from leadspipe.callrail import CallRailClient, FormSubmission


class Settings(BaseSettings):
    host: str = '0.0.0.0'
    port: int = 8001
    facebook_token: str
    callrail_account: str
    callrail_api_key: str


app = FastAPI(title='Leads Pipe')
logger = logging.getLogger(__name__)
settings = Settings()

facebook = FacebookClient(
    settings.facebook_token
)

callrail = CallRailClient(
    settings.callrail_account,
    settings.callrail_api_key
)


@app.get('/webhook', response_class=PlainTextResponse)
async def install(request: Request):
    payload = InstallPayload.of(request.query_params)
    logger.info('Challenge received: %s', str(payload))

    try:
        payload.verify(settings.facebook_verify_token)
        return payload.challenge
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid verify token')


@app.post('/webhook')
async def webhook(request: Request):
    payload = Lead.of(await request.json())
    form_submissions = await facebook.retrieve_form_submissions(payload)
    company_mapping = {
        company.name: company.id
        for company in await callrail.list_companies()
    }
    for form in form_submissions:
        form.company_id = company_mapping.get(form.page, None)

    await asyncio.gather(*[
        callrail.create_form_submission(form)
        for form in form_submissions
        if form.company_id is not None
    ])
    return {'ok': True}


if __name__ == '__main__':
    run(app, host=settings.host, port=settings.port)
