from rest_framework.views import APIView, Request, Response, status
from .models import Pet
from .serializers import PetSerializer
from groups.models import Group
from traits.models import Trait
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict

# Create your views here.
class PetView(APIView, PageNumberPagination):
    def get(self, request: Request) -> Response:
        pets = Pet.objects.all()
        result_page = self.paginate_queryset(pets, request)

        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        group_data = serializer.validated_data.pop('group')

        group, created = Group.objects.get_or_create(**group_data)

        traits_data = serializer.validated_data.pop('traits')

        pet = Pet.objects.create(**serializer.validated_data, group=group)

        for trait_item in traits_data:
            trait = Trait.objects.filter(name__icontains=trait_item["name"]).first()
            
            if not trait:
                trait = Trait.objects.create(**trait_item)
            
            pet.traits.add(trait)

        pet_serializer = PetSerializer(pet)

        return Response(pet_serializer.data, status.HTTP_201_CREATED)


class PetDetailView(APIView):
    def get(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(pet)

        return Response(serializer.data)
    

    def patch(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        group_data: dict = serializer.validated_data.pop("group", None)

        if group_data and pet.group["name"] != group_data["name"]:
            group, created = Group.objects.get_or_create(**group_data)
            pet.group = group
            import ipdb; ipdb.set_trace()
            pet.save()

        traits_data: dict = serializer.validated_data.pop("traits", None)
        if traits_data:
            pet.traits.clear()
            
            for trait in traits_data:
                data = Trait.objects.filter(name__icontains=trait["name"]).first()
                if not data:
                    data = Trait.objects.create(**trait)

                pet.traits.add(data)
            pet.save()
        
        serializer_response = PetSerializer(pet)

        return Response(serializer_response.data)


    def delete(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)

        pet.group = None
        pet.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
