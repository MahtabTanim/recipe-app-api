from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 6},
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        request = self.context.get("request")
        user = authenticate(request=request, username=email, password=password)
        if not user:
            msg = "unable to authenticate user"
            raise serializers.ValidationError(msg, code="authorization")
        attrs["user"] = user
        return attrs
