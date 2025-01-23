from typing import TypedDict, List, Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To, TemplateId
from sendgrid.helpers.mail.personalization import Personalization

from src.setup.config.settings import settings


class EmailDict(TypedDict):
    email: str
    name: str


class SendgridService:
    """send email using sendgrid"""

    def __new__(cls):
        if not settings.SENDGRID_API_KEY:
            raise Exception("Error: Sendgrid API Key not found")
        if not hasattr(cls, "instance"):
            cls.instance = super(SendgridService, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._api_key = settings.SENDGRID_API_KEY
        self._sgc = SendGridAPIClient(self._api_key)

    @staticmethod
    def _create_receiver_email(receivers: List[EmailDict]) -> List[To]:
        """converts receivers email dict to `To` class instance"""
        to_emails = []
        for receiver in receivers:
            to_emails.append(To(receiver["email"], receiver["name"]))
        return to_emails

    @staticmethod
    def _create_personalizations(receiver: To, template_dict: dict):
        """creates personalization for each receiver with its name"""
        template_name_dict = {"name": "", **template_dict}
        personalization = Personalization()
        personalization.add_to(receiver)
        template_name_dict["name"] = receiver.name
        personalization.dynamic_template_data = template_name_dict
        return personalization

    def _send_template_email(
        self,
        sender: str,
        receivers: List[EmailDict],
        template_id: TemplateId,
        template_dict: Optional[dict] = None,
    ):
        """
        ### send template email
        Args:
            sender - email of sender
            receivers: List[EmailDict] - email list of receiver(s)
            template_id: TemplateId - dynamic template's id
            template_dict: Optional[dict] - context to pass with the template
        """
        to_emails = self._create_receiver_email(receivers)
        mail = Mail(from_email=sender, to_emails=to_emails)
        if template_dict:
            mail._personalizations = []
            for receiver in to_emails:
                personalization = self._create_personalizations(receiver, template_dict)
                mail.add_personalization(personalization)
        mail.template_id = template_id
        response = self._sgc.send(mail)
        return response