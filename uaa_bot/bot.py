import time

from uaa_bot.notifier import Notifier
from uaa_bot.client import UAAClient
from uaa_bot.config import smtp, uaa


class UAABot:
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
        response = uaac.list_expiring_users(days_ago=days_ago)
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

    def _summary_response(self, title: str, users: list = []) -> dict:
        timestamp = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        return {
            "title": title,
            "timestamp": timestamp,
            "total_accounts": len(users),
            "user_summary": users,
        }

    def deactivate_users(
        self,
        days_ago: int = 90,
        days_range: int = 1,
        summary_title: str = "Deactivated users",
        start_of_day: int = None,
        end_of_day: int = None,
        params: dict = {},
    ) -> dict:
        users = []
        uaac = UAAClient(uaa_config=self.uaa_config)
        uaac.authenticate()

        if start_of_day and end_of_day:
            response = uaac.list_expiring_users(
                start_of_day=start_of_day, end_of_day=end_of_day, params=params
            )
        else:
            response = uaac.list_expiring_users(
                days_ago=days_ago, days_range=days_range, params=params
            )

        resources = response.get("resources")

        for user in resources:
            user_email = user.get("userName")
            user_guid = user.get("id")
            deactivated_response = uaac.deactivate_user(user)
            users.append({user_email, user_guid})

        summary = self._summary_response(summary_title, users)
        return summary

    def notify_and_deactivate(self) -> dict:
        """
        Notify and deactivate users after 90 days without logging into cloud.gov
        """
        users = []
        uaac = UAAClient(uaa_config=self.uaa_config)
        uaac.authenticate()
        response = uaac.list_expiring_users(days_ago=90, days_range=2)
        resources = response.get("resources")

        # Deactivate and send notification of account deactivation
        for user in resources:
            user_email = user.get("userName")
            user_guid = user.get("id")
            notification = Notifier(user_email)
            uaac.deactivate_user(user)
            notification.send_email("account_expired")
            users.append({user_email, user_guid})

        # Create and return summary of action
        summary = self._summary_response("Deactivation of accounts", users)
        return summary

    def notify_deactivation_in_1_day(self) -> dict:
        summary = self._notify_deactivation_x_days_ago(
            89, "Account of deactivations in 1 day", "account_expires_in_1_day"
        )
        return summary

    def notify_deactivation_in_10_days(self) -> dict:
        summary = self._notify_deactivation_x_days_ago(
            80, "Account of deactivations in 10 days", "account_expires_in_10_days"
        )
        return summary

    def get_all_user_last_logon(
        self,
        days_ago: int = 0,
        days_range: int = 365,
        summary_title: str = "List Users",
        start_of_day: int = None,
        end_of_day: int = None,
        params: dict = {},
    ) -> dict:
        """
        Gets list of users and their last logon info
        """
        users = []
        uaac = UAAClient(uaa_config=self.uaa_config)
        uaac.authenticate()
        if start_of_day and end_of_day:
            response = uaac.list_users_last_logon(
                start_of_day=start_of_day, end_of_day=end_of_day, params=params
            )
        else:
            response = uaac.list_users_last_logon(
                days_ago=days_ago, days_range=days_range, params=params
            )
        resources = response.get("resources")

        # Get user with their last logon info
        for user in resources:
            user_email = user.get("userName")
            user_guid = user.get("id")
            user_last_logon = time.ctime(user.get("lastLogonTime") / 1000)
            users.append(
                {
                    "user_email": user_email,
                    "user_guid": user_guid,
                    "user_last_logon": user_last_logon,
                }
            )

        # Create and return summary of users' last logon
        summary = self._summary_response_with_last_logon(summary_title, users)
        return summary

    def _summary_response_with_last_logon(self, title: str, users: list = []) -> dict:
        timestamp = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        return {
            "title": title,
            "timestamp": timestamp,
            "total_accounts": len(users),
            "user_summary": users,
        }
