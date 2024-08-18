import time
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import logging
import sys

class ClubInvitationSender:
    def __init__(self, username, password, invitation_url):
        self.logger = logging.getLogger('club-invitation-sender')
        self.logger.setLevel(logging.DEBUG)
        file_log_handler = logging.FileHandler('sent_invitations.log')
        file_log_handler.setLevel(logging.INFO)
        stdout_log_handler = logging.StreamHandler(sys.stdout)
        stdout_log_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_log_handler)
        self.logger.addHandler(stdout_log_handler)

        # Log format
        formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
        file_log_handler.setFormatter(formatter)
        stdout_log_handler.setFormatter(formatter)

        # Configure Chrome options
        options = ChromeOptions()
        options.add_argument('--user-data-dir={}/userdata'.format(os.getcwd()))  # Use user data if needed

        # Initialize the WebDriver
        print("Initializing ChromeDriver...")
        try:
            self.driver = webdriver.Chrome(options=options)  # Ensure ChromeDriver is in your PATH or specify the executable_path
            self.logger.info("ChromeDriver initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromeDriver: {e}")
            sys.exit(1)
        print("ChromeDriver initialized successfully.")

        # Retrieve credentials from environment variables
        self.username = username
        self.password = password
        self.invitation_url = invitation_url

        if not self.username or not self.password or not self.invitation_url:
            self.logger.error("Environment variables (username, password, invitation_url) are not properly set.")
            sys.exit(1)

        # Sample email addresses for testing
        self.emails = set()

    def login(self):
        """Log in to the site, handling Duo 2FA if necessary."""
        try:
            self.driver.get(self.invitation_url)
            self.logger.info(f"Opened URL: {self.invitation_url}")

            # Check if the email text box is already visible, indicating the user is already logged in
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="GroupInviteByEmail"]'))
                )
                self.logger.info("Already logged in. Email text box is visible.")
                return True
            except:
                self.logger.info("Email text box not visible. Proceeding with login.")

            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, 'username')))
            self.logger.info("Login page loaded.")

            self.driver.find_element(By.ID, 'username').send_keys(self.username)
            self.driver.find_element(By.ID, 'password').send_keys(self.password)
            self.driver.find_element(By.NAME, 'submit').click()
            self.logger.info("Login credentials submitted.")

            WebDriverWait(self.driver, 20).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@id="duo_iframe"]')))
            self.logger.info("Duo 2FA iframe loaded.")

            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="login-form"]/div[2]/div/label/input'))).click()
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//button[normalize-space()="Send Me a Push"]'))).click()
            self.logger.info('Duo 2FA push sent.')

            # Wait for "Yes, this is my device" button and click it
            self.driver.switch_to.default_content()  # Switch out of the iframe
            yes_button = WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Yes, this is my device")]')))
            yes_button.click()
            self.logger.info('Clicked "Yes, this is my device" button.')

            # Wait until the email textbox is visible
            WebDriverWait(self.driver, 60).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="GroupInviteByEmail"]')))
            self.logger.info("Email text box is visible, login successful.")

            return True
        except Exception as e:
            self.logger.error(f'Failed to log in: {e}')
            return False

    def add_emails_and_send_invitations(self):
        """Add emails to the form and send invitations."""
        try:
            # Locate the email textarea and enter the emails
            email_textarea = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="GroupInviteByEmail"]'))
            )
            email_textarea.send_keys("\n".join(self.emails))
            self.logger.info(f'Entered emails: {", ".join(self.emails)}')

            # Click the "Add Email" button
            add_email_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="GroupInviteByEmailSubmit"]'))
            )
            add_email_button.click()
            self.logger.info('Clicked "Add Email" button.')
            time.sleep(2)  # Pause to observe the action

            # Wait for the "Send Invitations" button to appear and click it
            send_invitation_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="invitationActions_sendButton"]'))
            )
            send_invitation_button.click()
            self.logger.info('Clicked "Send Invitations" button.')

            self.logger.info('Invitations sent successfully.')
            time.sleep(15)  # Pause to observe the action

        except Exception as e:
            self.logger.error(f'Error during the invitation process: {e}')

    def run(self):
        """Main function to handle the login and invitation process."""
        if self.login():
            try:
                self.add_emails_and_send_invitations()
            except Exception as e:
                self.logger.error(f'Error during the process: {e}')
            finally:
                self.driver.quit()  # Ensure the browser closes after the script completes
