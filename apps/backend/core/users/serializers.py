from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Subscription
from datetime import timedelta
from django.utils import timezone

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'username', 'password', 'password_confirm')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Credenciais inválidas.')
            if not user.is_active:
                raise serializers.ValidationError('Usuário desativado.')
            
            # Atualizar último login
            user.last_login_at = timezone.now()
            user.save(update_fields=['last_login_at'])
            
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Email e senha são obrigatórios.')
        
        return attrs

class UserSerializer(serializers.ModelSerializer):
    subscription_status = serializers.ReadOnlyField()
    is_in_trial_period = serializers.ReadOnlyField()
    has_active_access = serializers.ReadOnlyField()
    days_until_trial_end = serializers.SerializerMethodField()
    days_until_subscription_end = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'username',
            'subscription_status', 'is_in_trial_period', 'has_active_access',
            'data_inicio_teste', 'data_fim_teste', 'plano_ativo',
            'data_inicio_plano', 'data_fim_plano', 'days_until_trial_end',
            'days_until_subscription_end', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'subscription_status', 'is_in_trial_period', 'has_active_access')
    
    def get_days_until_trial_end(self, obj):
        if obj.data_fim_teste and obj.is_in_trial_period:
            delta = obj.data_fim_teste - timezone.now()
            return max(0, delta.days)
        return 0
    
    def get_days_until_subscription_end(self, obj):
        if obj.data_fim_plano and obj.plano_ativo:
            delta = obj.data_fim_plano - timezone.now()
            return max(0, delta.days)
        return 0

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError('Usuário não encontrado com este email.')
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs

class SubscriptionSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    days_until_renewal = serializers.ReadOnlyField()
    
    class Meta:
        model = Subscription
        fields = (
            'id', 'user', 'user_email', 'status', 'plan_name', 'plan_price',
            'plan_currency', 'plan_interval', 'current_period_start',
            'current_period_end', 'days_until_renewal', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'days_until_renewal')

class StripeCheckoutSessionSerializer(serializers.Serializer):
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()
    
    def validate(self, attrs):
        # Validar se o usuário não tem plano ativo
        user = self.context['request'].user
        if user.plano_ativo:
            raise serializers.ValidationError('Usuário já possui plano ativo.')
        return attrs
