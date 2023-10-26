from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response


class CreateDestroyM2MMixin:
    def create_m2m(self, read_serializer,
                   user_field_name, user_related_name, lookup_field_name,
                   create_error_message):
        serializer = self.get_serializer(data={
            user_field_name: self.request.user.pk,
            lookup_field_name: self.kwargs['pk']
        })
        serializer.is_valid(raise_exception=True)
        if getattr(self.request.user, user_related_name).filter(
                **{lookup_field_name: self.get_object()}
        ).exists():
            raise ValidationError(create_error_message)
        return Response(
            read_serializer(
                getattr(serializer.save(), lookup_field_name),
                context={'request': self.request}
            ).data,
            status=status.HTTP_201_CREATED
        )

    def destroy_m2m(self, user_related_name,
                    lookup_field_name, lookup_model,
                    destroy_error_message):
        obj = getattr(self.request.user, user_related_name).filter(
            **{lookup_field_name: get_object_or_404(
                lookup_model,
                pk=self.kwargs['pk']
            )}
        )
        if not obj.exists():
            raise ValidationError(destroy_error_message)
        obj.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
