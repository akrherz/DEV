"""
Here we are, writing some selenium-based twitter bot.  This is not the life we
wanted, but the life we got.

TODO:
  - Add crude message queue reading support.
"""
import argparse
from datetime import timedelta
import glob
import json
from multiprocessing.pool import ThreadPool
import os
import random
import time
import traceback

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from pyiem.util import utc

XPATH_TWEETBOX = "//div[contains(@class, 'public-DraftStyleDefault-block')]"


class TwitterWebSession:
    """A bot acting like a human on the twitters."""

    def __init__(self, username, password):
        """Constructor."""
        self.username = username
        self.password = password
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--headless")
        options.add_argument(f"--user-data-dir=botdata/{username}/chrome")
        # Create a new instance of the Chrome driver.
        self.driver = webdriver.Chrome(options=options)
        self.authenticated = False

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
                with open(filename, encoding="utf-8") as fp:
                    payload = json.load(fp)
                self.tweet(payload["msg"], None)
            except Exception as exp:
                self.log(exp)
                traceback.print_exc()
            os.unlink(filename)

    def tweet(self, msg, filename):
        """Send a tweet."""
        self.log("Tweeting {msg}")
        elem = self.get_tweetbox()
        elem.send_keys(msg)
        if filename is not None:
            elem = self.driver.find_element(By.XPATH, "//input[@accept]")
            elem.send_keys(filename)

        btn = self.driver.find_element(
            By.XPATH, "//div[@data-testid='tweetButtonInline']"
        )
        btn.click()


def bot(username, password):
    """Run a bot for a long time, in a thread even."""
    # Ensure we have a working directory
    os.makedirs(f"botdata/{username}/chrome", exist_ok=True)
    # Initial jitter
    # 1) Prevent server-DOS invoking 160 instances of Chrome
    # 2) Prevent a block from twitter, hopefully
    time.sleep(random.randint(1, 600))
    try:
        iembot = TwitterWebSession(username, password)
        # This should bring us to the homepage
        iembot.login()
        # Park on a page without any network interaction
        iembot.driver.get("https://twitter.com/en/tos")
        last_activity = utc()
        # Main-loop iter will speed up and slow down based on usage
        delay = 15  # seconds
        while True:
            delay = min([3600, delay + 60])
            time.sleep(delay)
            # Wake up, do we have tweeting to do?
            if iembot.process_tweets():
                last_activity = utc()
            if (utc() - last_activity) < timedelta(hours=2):
                continue
            last_activity = utc()
            # Make some activity
            iembot.driver.get("https://twitter.com/")
            time.sleep(33)
            # Park on a page without any network interaction
            iembot.driver.get("https://twitter.com/en/tos")

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
    with ThreadPool(args.threads) as pool:
        for user in users:
            pool.apply_async(bot, user)
        pool.close()
        pool.join()


if __name__ == "__main__":
    main()
