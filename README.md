Amazon Price Tracker Telegram Bot
Here is Direct LInk to my Working TelegramBot
https://t.me/AmazedTrackerBot

A simple yet powerful Telegram bot that monitors Amazon product pages and notifies you when the price drops. Built with Python and deployed on Google Cloud Run.

✨ Features
24/7 Price Monitoring: The bot runs continuously, checking prices at regular intervals.

Instant Price Drop Alerts: Get a Telegram message the moment a price decreases.

Unlimited Product Tracking: Track as many products as you want.

Price History: The /list command shows the current, highest, and lowest recorded prices for each item.

Affiliate Link Integration: Automatically converts product links to use your Amazon Associates tag.

🚀 Deployment Guide (Google Cloud Run)
Follow these steps to deploy your own instance of the bot.

Part 1: Prerequisites
A GitHub Account: Where you'll store your code.

A Google Cloud Platform (GCP) Account: With billing enabled. New users get a generous free tier and credits.

Google Cloud SDK (gcloud): Installed and initialized on your local machine. Follow the official installation guide.

Part 2: Initial Setup
Step 1: Create a Telegram Bot
Open Telegram and search for the @BotFather user.

Start a chat and send /newbot.

Follow the prompts to choose a name and username for your bot.

BotFather will give you a token. It will look something like 1234567890:ABCdEFG-hIjKlMnOpQrStUvWxYz.

Save this token! You will need it later.

Step 2: Get Your Amazon Affiliate Tag
Sign up for the Amazon Associates Program for your region (e.g., Amazon.in).

Once approved, you will find your Tracking ID (or "tag") on your Associates dashboard. It usually ends in -21 for India.

Save this tag!

Step 3: Get the Code
Clone this repository to your local machine:

Bash

git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
cd YOUR_REPOSITORY_NAME
Part 3: Deployment to Google Cloud Run
We will use Google Cloud Run, a serverless platform that is perfect for this kind of bot. It's cost-effective because it can scale to zero when idle.

Step 1: Enable Required APIs
In the Google Cloud Console or using the gcloud CLI, enable the Cloud Build API and the Cloud Run Admin API.

Bash

gcloud services enable run.googleapis.com cloudbuild.googleapis.com
Step 2: Build the Container Image
This command tells Google Cloud Build to use your Dockerfile to package the application into a container image and store it in the Artifact Registry. Replace [PROJECT_ID] with your actual Google Cloud Project ID.

Bash

gcloud builds submit --tag gcr.io/[PROJECT_ID]/amazon-price-bot
Step 3: Deploy to Cloud Run
This is the final command. It deploys your container image to Cloud Run and securely injects your secret token and affiliate tag as environment variables.

Replace [PROJECT_ID] with your Google Cloud Project ID.

Replace [YOUR_TELEGRAM_BOT_TOKEN] with the token from BotFather.

Replace [YOUR_AMAZON_AFFILIATE_TAG] with your Amazon Associates tag.

You can choose a [REGION] close to you, like asia-south1 (Mumbai) or us-central1.

Bash

gcloud run deploy amazon-price-bot \
  --image gcr.io/[PROJECT_ID]/amazon-price-bot \
  --platform managed \
  --region [REGION] \
  --set-env-vars="TELEGRAM_TOKEN=[YOUR_TELEGRAM_BOT_TOKEN]" \
  --set-env-vars="AFFILIATE_TAG=[YOUR_AMAZON_AFFILIATE_TAG]" \
  --allow-unauthenticated
Note: The --allow-unauthenticated flag is used here for simplicity. Since the bot is only activated by its polling mechanism and Telegram's webhooks, direct HTTP access is not a primary security concern. For enhanced security, you could set up VPC connectors and firewall rules.

Part 4: You're Done!
That's it! Your bot is now running on Google Cloud. Open Telegram, find your bot, and send it an Amazon link to start tracking.

After pasting this into the README.md file on GitHub, commit the new file. Your repository is now complete and professional-looking, with all the code and instructions needed for anyone (including yourself) to deploy it.
