# Server setup

- Install Python 3.8. On recent version of Ubuntu you can do

        sudo apt install python3.8 py38-setuptools py38-venv

- Install Poetry

        sudo pip3.8 install poetry

- Upload the code to your server
- Install the dependencies with

        poetry install

- Create a configuration file named `.env` with the following parameters

    | Name                  | Description                   | Note          |
    |-----------------------|-------------------------------|---------------|
    | FACEBOOK_APP_ID       | Facebook Application ID       | Required      |
    | FACEBOOK_APP_SECRET   | Facebook Application Secret   | Required      |
    | FACEBOOK_VERIFY_TOKEN | Facebook Webhook verify token | Random string |
    | CALLRAIL_ACCOUNT      | CallRail Account number       | Required      |
    | CALLRAIL_API_KEY      | CallRail API Key              | Required      |
    | HOST                  | Server host                   | Optional      |
    | PORT                  | Server port                   | Optional      |

- Create a SystemD service file. An example is provided in
  `config/leadspipe.service`

- If you're planning to run the server behind reverve proxies such as Nginx,
  please do configure it. HTTPS is required to run Webhook. The default server
  Uvcorn also has support for it, if you want to run HTTPS with the default
  server instead of Nginx, please consult its documentation:

  https://www.uvicorn.org/settings/#https

- Install the service by copying that file to `/etc/systemd/system`
- Enable and start the server

        sudo systemctl enable leadspipe
        sudo systemctl start leadspipe

- Verify that the server is up and running:

        sudo journalctl -fu leadspipe

# Facebook App setup

- Create a new Facebook App
- Setup the required parameter for the app: (these are important as the app need
  to go through permission approval by Facebook)
  - App domains
  - Privacy Policy URL
  - Terms of Service URL
- Configure WebHook:
  - At PRODUCT menu, select the + button
  - Choose WebHook
  - Fill in the following information:
    - URL: https://<your domain>.com/webhook
    - Verify token: the token you have configured the app with (in
      `FACEBOOK_VERIFY_TOKEN`)
  - Create a subscription
    - Choose Page object
    - Subscribe to the leadgen field
- Install the app to the page you desired

# Testing

- Create a lead form for your page:
  - Go to Publishing Tools
  - Choose Forms Library
  - Create

- https://developers.facebook.com/tools/lead-ads-testing
