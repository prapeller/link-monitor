import pytest
from pydantic.error_wrappers import ValidationError

from database.models.tag import TagModel
from database.schemas.tag import TagCreateSerializer

tag_country_gb_serializer = TagCreateSerializer(name='gb', ref_property='country')
tag_country_czh_serializer = TagCreateSerializer(name='czh', ref_property='country')
tag_language_eng_serializer = TagCreateSerializer(name='eng', ref_property='language')


def test_can_create_tags(repo_in_memory):
    """test tags can be created"""
    repo = repo_in_memory

    tag_country_gb = repo.create(TagModel, tag_country_gb_serializer)
    tag_country_czh = repo.create(TagModel, tag_country_czh_serializer)
    tag_language_eng = repo.create(TagModel, tag_language_eng_serializer)

    tags = repo.get_all(TagModel)

    assert tags == [tag_country_gb, tag_country_czh, tag_language_eng]


def test_tag_name_not_longer_then_3_symbols(repo_in_memory):
    """test tags names have 4 symbols max otherwise validation error occures"""
    repo = repo_in_memory

    with pytest.raises(ValidationError, match='Tag length should not be longer than 3 characters.') as exc_info:
        repo.create(TagModel, TagCreateSerializer(name='china', ref_property='country'))
        raise ValidationError


def test_tag_name_capitalize(repo_in_memory):
    """test tags names capitalizes"""
    repo = repo_in_memory

    eng_tag = repo.create(TagModel, TagCreateSerializer(name='eng', ref_property='country'))
    assert eng_tag.name == 'ENG'


def test_tag_removes_non_alphabetic(repo_in_memory):
    """test all non-alphabetic characters are being removed from tag name"""
    repo = repo_in_memory

    eng_tag = repo.create(TagModel, TagCreateSerializer(name='!en', ref_property='country'))
    assert eng_tag.name == 'EN'
    eng_tag = repo.create(TagModel, TagCreateSerializer(name='2ru', ref_property='country'))
    assert eng_tag.name == 'RU'
