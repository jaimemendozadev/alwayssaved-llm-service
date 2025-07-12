from mistralai import Mistral

from server.utils.aws.ssm import get_secret

MISTRAL_API_KEY = get_secret("/alwayssaved/MISTRAL_API_KEY")

client = Mistral(api_key=MISTRAL_API_KEY)
