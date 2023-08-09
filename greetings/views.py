from oauth2_provider.decorators import protected_resource
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from greetings.models import Greeting
from greetings.serializers import GreetingSerializer
from greetings.utils.constants import CUSTOM_GOODBYE
from greetings.utils.responses import GreetingErrorResponse, GreetingSuccessResponse
from greetings.utils.services import GreetingService, RecursiveViewService
from greetings.utils.validators import GreetingParamValidator


@api_view(["GET"])
@protected_resource(scopes=["read"])
def list_greetings(request: Request) -> Response:
    """List all the greetings from the db."""

    greetings = Greeting.objects.all()
    serializer = GreetingSerializer(greetings, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@protected_resource(scopes=["write"])
def save_custom_greeting(request: Request) -> Response:
    """Save a custom greeting from a user."""

    try:
        custom_greeting = GreetingParamValidator(request)
        if custom_greeting == CUSTOM_GOODBYE:
            return GreetingSuccessResponse(
                status_code=status.HTTP_201_CREATED,
                data={"greeting": request.data["greeting"], "goodbye": custom_greeting},
            )

        GreetingService.create_and_save(custom_greeting)
        return RecursiveViewService.make_recursive_call(request)

    except Exception as exc:
        return GreetingErrorResponse(data={"detail": str(exc)})
