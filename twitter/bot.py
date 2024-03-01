"""
Here we are, writing some selenium-based twitter bot.  This is not the life we
wanted, but the life we got.

"""

import argparse
import glob
import json
import os
import random
import tempfile
import time
import traceback
from datetime import datetime, timedelta, timezone
from multiprocessing.pool import ThreadPool

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pyiem.util import utc

XPATH_TWEETBOX = "//div[contains(@class, 'public-DraftStyleDefault-block')]"
LATENCY_THRES = timedelta(minutes=10)


class TwitterWebSession:
    """A bot acting like a human on the twitters."""

    def __init__(self, username, password, interactive=False):
        """Constructor."""
        self.username = username
        self.password = password
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        if not interactive:
            options.add_argument("--headless")
        options.add_argument(f"--user-data-dir=botdata/{username}/chrome")
        # Create a new instance of the Chrome driver.
        self.driver = webdriver.Chrome(options=options)
        self.authenticated = False
        self.delqueue = []

    def log(self, msg):
        """Log something."""
        fn = f"botdata/{self.username}/{self.username}.log"
        msg = f"{utc():%Y-%m-%dT%H:%M:%SZ} [{self.username}] {msg}"
        with open(fn, "a", encoding="utf-8") as fh:
            fh.write(f"{msg}\n")
        print(msg)

    def login(self):
        """See if we can log in!"""
        self.log("Login called...")
        attempt = 1
        # Get the homepage
        self.driver.get("https://twitter.com")
        # Jitter
        time.sleep(random.randint(2, 10))
        if self.get_tweetbox() is not None:
            self.authenticated = True
        while not self.authenticated and attempt < 5:
            self.driver.save_screenshot(
                f"botdata/{self.username}/{self.username}_loginpage.png"
            )
            self.driver.get("https://twitter.com/i/flow/login")
            time.sleep(random.randint(1, 10))

            try:
                self.log(f"Sending username, attempt {attempt}")
                WebDriverWait(self.driver, 30).until(
                    EC.visibility_of_element_located((By.TAG_NAME, "input"))
                ).send_keys(self.username + Keys.ENTER)
                # Add some random jitter
                time.sleep(random.randint(2, 20))
                self.log(f"Sending password, attempt {attempt}")
                WebDriverWait(self.driver, 30).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, "//input[@type='password']")
                    )
                ).send_keys(self.password + Keys.ENTER)
                time.sleep(random.randint(2, 20))
                # Send arb escape to see if that can clear a popup
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.ESCAPE)
                actions.perform()
                if self.get_tweetbox() is not None:
                    self.authenticated = True
                    break
            except TimeoutException:
                self.log("failed to load login page.")
            attempt += 1
        self.driver.save_screenshot(
            f"botdata/{self.username}/{self.username}_afterlogin.png"
        )

    def get_tweetbox(self):
        """Effective Login check by looking for the tweetbox."""
        elem = None
        try:
            elem = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, XPATH_TWEETBOX))
            )
        except TimeoutException:
            pass
        return elem

    def process_tweets(self) -> bool:
        """Process anything queued."""
        filenames = glob.glob(f"botdata/{self.username}/tweet*.json")
        if not filenames:
            return False
        # Ensure we are at the homepage
        self.driver.get("https://twitter.com")
        time.sleep(random.randint(2, 10))
        # Process files written here
        for filename in filenames:
            try:
                stamp = filename.split("_")[-1][:15]
                ts = datetime.strptime(stamp, "%Y%m%dT%H%M%S")
                if (utc() - ts.replace(tzinfo=timezone.utc)) < LATENCY_THRES:
                    with open(filename, encoding="utf-8") as fp:
                        payload = json.load(fp)
                    self.tweet(payload["msg"], payload.get("media"))
                else:
                    self.log(f"Ignoring tweet {filename} as too old")
            except Exception as exp:
                self.log(exp)
                traceback.print_exc()
            os.unlink(filename)

    def tweet(self, msg, media):
        """Send a tweet."""
        self.log(f"Tweeting {msg}")
        elem = self.get_tweetbox()
        # Wait for the element to be ready?
        time.sleep(random.randint(1, 6))
        # Try to get the entry box ready for action?
        elem.send_keys(f"{utc():%f}" + Keys.BACKSPACE + Keys.BACKSPACE)
        elem.send_keys(Keys.BACKSPACE + Keys.BACKSPACE + Keys.BACKSPACE)
        time.sleep(random.randint(1, 6))
        elem.send_keys(Keys.BACKSPACE + Keys.BACKSPACE + Keys.BACKSPACE)
        # Slow down typing as something happens
        for char in msg.replace("iem.local", "mesonet.agron.iastate.edu"):
            elem.send_keys(char)
            time.sleep(random.randint(0, 10) * 0.01)

        time.sleep(random.randint(1, 3))

        if media is not None:
            try:
                # We are in a thread, so we should be able to block
                req = requests.get(media, timeout=120)
                with tempfile.NamedTemporaryFile(
                    "wb", delete=False, suffix=".png"
                ) as tmpfp:
                    tmpfp.write(req.content)
                elem = self.driver.find_element(By.XPATH, "//input[@accept]")
                elem.send_keys(tmpfp.name)
                self.delqueue.append(tmpfp.name)
            except Exception as exp:
                self.log(exp)
                self.log(media)

        btn = self.driver.find_element(
            By.XPATH, "//div[@data-testid='tweetButtonInline']"
        )
        # This worksaround having some modal intercepting the click...
        self.driver.execute_script("arguments[0].click();", btn)


def bot(username, password, interactive, init_delay_max=600):
    """Run a bot for a long time, in a thread even."""
    # Ensure we have a working directory
    os.makedirs(f"botdata/{username}/chrome", exist_ok=True)
    # Initial jitter
    # 1) Prevent server-DOS invoking 160 instances of Chrome
    # 2) Prevent a block from twitter, hopefully
    time.sleep(random.randint(1, init_delay_max))
    try:
        iembot = TwitterWebSession(username, password, interactive)
        # This should bring us to the homepage
        iembot.login()
        # Park on a page without any network interaction
        iembot.driver.get("https://twitter.com/en/tos")
        last_activity = utc()
        delay = 15
        while True:
            # micro-optimization
            delay = min([delay, 120])
            time.sleep(delay)
            delay += 5
            # Wake up, do we have tweeting to do?
            if iembot.process_tweets():
                last_activity = utc()
                delay = 15
            if (utc() - last_activity) < timedelta(hours=2):
                continue
            last_activity = utc()
            # Make some activity
            iembot.driver.get("https://twitter.com/")
            time.sleep(random.randint(20, 40))
            # Park on a page without any network interaction
            iembot.driver.get("https://twitter.com/en/tos")
            while iembot.delqueue:
                fn = iembot.delqueue.pop(0)
                if os.path.isfile(fn):
                    os.unlink(fn)

    except Exception as exp:
        iembot.log(exp)
        traceback.print_exc()
    iembot.driver.save_screenshot(f"botdata/{username}/{username}_final.png")
    iembot.driver.quit()


def main():
    """Go Main Go."""
    parser = argparse.ArgumentParser(
        prog="Bot",
        description="A selenium-based Twitter Bot for legal purposes.",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Start chrome in non-headless display to allow interaction.",
    )
    parser.add_argument(
        "-t", "--threads", type=int, help="Threads to start", default=256
    )
    parser.add_argument(
        "-u", "--user", help="Twitter screen-name to limit process to."
    )
    args = parser.parse_args()
    users = []
    with open("accounts.txt", encoding="ascii") as fh:
        for line in fh:
            tokens = line.strip().split()
            if len(tokens) != 2:
                continue
            if args.user is not None and args.user != tokens[0]:
                continue
            users.append(tokens)
    init_delay_max = 600 if args.user is None else 2
    with ThreadPool(args.threads) as pool:
        for user in users:
            pool.apply_async(bot, (*user, args.interactive, init_delay_max))
        pool.close()
        pool.join()


if __name__ == "__main__":
    main()
