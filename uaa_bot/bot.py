import time

from uaa_bot.notifier import Notifier
from uaa_bot.client import UAAClient
from uaa_bot.config import smtp, uaa


class UAABot(object):
    """
    The bot to notify and deactivate accounts
    """

    def __init__(self, smtp_config: dict = smtp, uaa_config: dict = uaa):
        self.smtp_config = smtp_config
        self.uaa_config = uaa_config

    def _notify_deactivation_x_days_ago(
        self, days_ago: int, summary_title: str, template_name: str
    ) -> dict:
        """
        Notifies users after x numbers days without logging into cloud.gov
        of account deactivation soon
        """
        users = []
        uaac = UAAClient(uaa_config=self.uaa_config)
        uaac.authenticate()
        response = uaac.list_expiring_users(90)
        resources = response.get("resources")

        # Deactivate and send notification of account deactivation
        for user in resources:
            user_email = user.get("userName")
            user_guid = user.get("id")
            notification = Notifier(user_email)
            notification.send_email(template_name)
            users.append({"user_email": user_email, "user_guid": user_guid})

        # Create and return summary of action
        summary = self._summary_response(summary_title, users)
        return summary

    def _summary_response(self, title: str, users: dict) -> dict:
        timestamp = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        return {
            "title": title,
            "timestamp": timestamp,
            "total_accounts": len(users),
            "user_summary": users,
        }

    def notify_and_deactivate(self) -> dict:
        """
        Notify and deactivate users after 90 days without logging into cloud.gov
        """
        try:
            users = []
            uaac = UAAClient(uaa_config=self.uaa_config)
            uaac.authenticate()
            response = uaac.list_expiring_users(90)
            resources = response.get("resources")

            # Deactivate and send notification of account deactivation
            for user in resources:
                user_email = user.get("userName")
                user_guid = user.get("id")
                notification = Notifier(user_email)
                uaac.deactivate_user(user_guid)
                notification.send_email("account_expired")
                users.append({user_email, user_guid})

            # Create and return summary of action
            summary = self._summary_response("Deactivation of accounts", users)
            return summary

        except Exception as e:
            raise (e)

    def notify_deactivation_in_1_day(self) -> dict:
        try:
            summary = self._notify_deactivation_x_days_ago(
                89, "Account of deactivations in 1 day", "account_expires_in_1_day"
            )
            return summary
        except Exception as e:
            raise (e)

    def notify_deactivation_in_10_days(self) -> dict:
        try:
            summary = self._notify_deactivation_x_days_ago(
                80, "Account of deactivations in 10 days", "account_expires_in_10_days"
            )
            return summary
        except Exception as e:
            raise (e)
