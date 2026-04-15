from rest_framework.decorators import api_view
from rest_framework.response import Response
from services.categorization_service import CategorizationService


@api_view(['POST'])
def categorize_transaction(request):
    service = CategorizationService()

    transaction = {
        "description": request.data.get("description"),
        "vendor": request.data.get("vendor")
    }

    company = request.data.get("company")

    result = service.categorize(transaction, company)

    return Response(result)