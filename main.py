# main.py

import logging
import re
import asyncio
import os
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import (Application, CommandHandler, ContextTypes,
                          MessageHandler, filters)

# --- Configuration ---
# Load credentials from environment variables for security
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AFFILIATE_TAG = os.getenv("AFFILIATE_TAG", "amazingde0df9-21") # Default tag if not set
DATA_FILE = Path("data.json")

# --- Logging Setup ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Data Persistence ---
def load_data():
    """Loads tracked products from a JSON file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {} # Return empty dict if file is corrupted or empty
    return {}

def save_data(data):
    """Saves tracked products to a JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

tracked_products = load_data()

# --- Helper Functions (Your existing functions go here) ---
# NOTE: I've omitted the helper functions (get_product_info, create_affiliate_link)
# for brevity. Copy your original functions here. They are correct.
def get_product_info(url: str) -> dict:
    """Scrapes the Amazon product page for the title and price."""
    # Using more realistic browser headers to avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Request to {url} returned status code {response.status_code}")
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        title_element = soup.find(id="productTitle")
        title = title_element.get_text().strip() if title_element else "Title not found"
        price_element = soup.find("span", class_="a-price-whole")
        price_fraction_element = soup.find("span", class_="a-price-fraction")
        if price_element:
            price_str = price_element.get_text().strip().replace(",", "")
            if price_fraction_element:
                price_str += price_fraction_element.get_text().strip()
            price = float(re.sub(r"[^\d.]", "", price_str))
        else:
            price = None
        if title == "Title not found" or price is None:
            logger.warning("Could not find title or price. Page layout may have changed.")
            return None
        return {"title": title, "price": price, "url": url}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching product info: {e}")
        return None
    except (AttributeError, ValueError) as e:
        logger.error(f"Error parsing product info: {e}")
        return None

def create_affiliate_link(url: str, tag: str) -> str:
    """Appends the affiliate tag to a URL correctly."""
    if not tag:
        return url
    if '?' in url:
        return f"{url}&tag={tag}"
    else:
        return f"{url}?tag={tag}"


# --- Price Checker Background Task ---
async def price_checker(context: ContextTypes.DEFAULT_TYPE):
    """Periodically checks the price of all tracked products."""
    global tracked_products
    logger.info("Running periodic price check...")
    # Create a copy to avoid issues with modifying the dict while iterating
    for chat_id, products in list(tracked_products.items()):
        for product_url, product_data in list(products.items()):
            new_info = get_product_info(product_url)
            if new_info and new_info["price"] is not None:
                current_price = new_info["price"]
                old_price = product_data["price"]

                # Update high/low prices
                product_data["high_price"] = max(product_data.get("high_price", old_price), current_price)
                product_data["low_price"] = min(product_data.get("low_price", old_price), current_price)

                if current_price < old_price:
                    affiliate_link = create_affiliate_link(product_url, AFFILIATE_TAG)
                    message = (
                        f"PRICE DROP ALERT! 📉 GO GO GO!\n\n"
                        f"**{new_info['title']}**\n\n"
                        f"😭 Old Price: ₹{old_price}\n"
                        f"🤩 **New Price: ₹{current_price}**\n\n"
                        f"Grab it here: {affiliate_link}"
                    )
                    await context.bot.send_message(chat_id=chat_id, text=message)
                    product_data["price"] = current_price # Update the price in our records
    
    save_data(tracked_products) # Save any changes to disk
    logger.info("Price check finished.")

# --- Telegram Bot Command Handlers (Your handlers go here) ---
# NOTE: I've omitted the command handlers (start, help_command, etc.)
# for brevity. Copy your original functions here, but remember to call
# `save_data(tracked_products)` at the end of `track_product` and `list_tracked`.

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hey there! 👋 I'm your personal Amazon deal finder. Send me an Amazon product link to get started!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Just send me a link to an Amazon product and I'll start tracking it. Use `/list` to see your tracked items.")

async def list_tracked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.message.chat_id)
    if chat_id in tracked_products and tracked_products[chat_id]:
        message = "Here's what I'm tracking for you: 👀\n\n"
        for i, (url, data) in enumerate(tracked_products[chat_id].items(), 1):
            message += (
                f"{i}. **{data['title']}**\n"
                f"   - Now: **₹{data['price']}**\n"
                f"   - Highest: ₹{data['high_price']}\n"
                f"   - Lowest: ₹{data['low_price']}\n\n"
            )
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("You're not tracking any products yet. Send me an Amazon link to get started! 🚀")

async def track_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    if "amazon" not in url:
        await update.message.reply_text("Hmm, that doesn't look like an Amazon link. Please try again! 🤔")
        return

    await update.message.reply_text("On it! Let me check this product out... 🕵️‍♂️")
    product_info = get_product_info(url)
    if product_info and product_info["price"] is not None:
        chat_id = str(update.message.chat_id)
        if chat_id not in tracked_products:
            tracked_products[chat_id] = {}
        
        current_price = product_info['price']
        product_info['high_price'] = current_price
        product_info['low_price'] = current_price
        tracked_products[chat_id][url] = product_info
        
        save_data(tracked_products) # Persist the new product
        
        affiliate_link = create_affiliate_link(url, AFFILIATE_TAG)
        confirmation_message = (
            f"Awesome! I've added this to your tracking list. 👀\n\n"
            f"**{product_info['title']}**\n"
            f"Current Price: **₹{current_price}**\n\n"
            f"I'll let you know when the price drops! 📉"
        )
        await update.message.reply_text(confirmation_message)
    else:
        await update.message.reply_text("Sorry, I couldn't get the details for that product. Please check the link. 😥")

# --- Main Bot Setup ---
def main() -> None:
    """Sets up and runs the bot."""
    if not TELEGRAM_TOKEN:
        logger.error("FATAL: TELEGRAM_TOKEN environment variable not set.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_tracked))

    # Add message handler for tracking links
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_product))

    # Add the periodic price checker job
    job_queue = application.job_queue
    job_queue.run_repeating(price_checker, interval=3600, first=10) # Checks every hour, starts after 10s

    # Start the Bot
    application.run_polling()


if __name__ == "__main__":
    main()