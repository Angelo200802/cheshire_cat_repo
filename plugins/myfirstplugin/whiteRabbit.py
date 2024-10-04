from cat.mad_hatter.decorators import tool,hook
import requests
import re
import random

@tool
def ring_alarm(wait_time, cat):
    """Useful to ring the alarm. Use it whenever the user wants to ring the alarm. Input is the wait time of the alarm in seconds.""" 

    # Mocking alarm API call
    def ring_alarm_api():
        print("Riiing")

    cat.white_rabbit.schedule_job(ring_alarm_api, seconds=int(wait_time))

    return f"Alarm ringing in {wait_time} seconds"
@tool(return_direct=True)
def schedule_quote_scraper(interval, cat):
    """
    Useful to get a random quote at a scheduled interval. The interval is in seconds
    """
    def scrape_random_quote():
        url = "http://quotes.toscrape.com/"
        response = requests.get(url)
        response.raise_for_status()
        # We would normally use beautifulsoup here, but for this example we'll just use regex
        quotes = re.findall(r'<span class="text" itemprop="text">(.*?)</span>', response.text)
        if quotes:
            random_quote = random.choice(quotes)
            cat.send_ws_message(random_quote, msg_type="chat")
        else:
            cat.send_ws_message("No quotes found", msg_type="chat")

    # Schedule the job to run at the specified interval
    job_id = cat.white_rabbit.schedule_interval_job(scrape_random_quote, seconds=int(interval))
    print(job_id)
    return f"Quote scraping job scheduled to run every {interval} seconds."

@tool(return_direct=True)
def remove_scheduled_job(job_id,cat):
	"""
	Useful to remove a scheduled job. The job id is the input.
	"""
	cat.white_rabbit.remove_job(job_id)
	return f"{job_id} is cancelled."

