from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import TestCase, TestCaseResult, TestTask, ParentCateName, CateFolder, User


class TestCaseSerializer(ModelSerializer):
    case_belongs_system = SerializerMethodField(read_only=True)
    case_belongs = SerializerMethodField(read_only=True)

    class Meta:
        model = TestCase
        fields = ['id', 'create_worker', 'create_time', 'case_name', 'case_number', 'case_level', 'case_modify_time',
                  'case_belongs', 'case_pre',
                  'case_process', 'case_expect', 'case_belongs_system', 'case_modify_worker']

    def get_case_belongs_system(self, obj):
        folder = CateFolder.objects.get(id=obj.case_belongs)
        system_name = ParentCateName.objects.get(id=folder.parent)
        return system_name.part

    def get_case_belongs(self, obj):
        return CateFolder.objects.get(id=obj.case_belongs).folder_name


class TestCaseResultSerializer(ModelSerializer):
    class Meta:
        model = TestCaseResult
        exclude = ['logs']


class TestCaseResultLogSerializer(ModelSerializer):
    class Meta:
        model = TestCaseResult
        exclude = []


class TestTaskSerializer(ModelSerializer):
    class Meta:
        model = TestTask
        exclude = []


class FirstLevelTreeSerializer(ModelSerializer):
    class Meta:
        model = ParentCateName
        exclude = []


class FolderSerializer(ModelSerializer):
    class Meta:
        model = CateFolder
        exclude = []


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = []

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        if 'password' in validated_data.keys():
            user.set_password(validated_data['password'])
        user.save()
        return user


class ParentNameSerializer(ModelSerializer):
    class Meta:
        model = ParentCateName
        exclude = []
