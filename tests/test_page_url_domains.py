from core.dependencies import pudomain_params_dependency
from core.shared import filter_query_by_model_params_pudomain
from services.domain_checker.domain_checker import recreate_domains
from database.models.link import LinkModel
from database.models.page_url_domain import PageUrlDomainModel
from database.models.tag import TagModel
from database.schemas.link import LinkCreateSerializer
from database.schemas.tag import TagCreateSerializer

link_1_serializer = LinkCreateSerializer(
    page_url='https://donor-name1.com/url',
    anchor='anchor_text1',
    link_url='https://project-name1.com/url/',
)

link_2_serializer = LinkCreateSerializer(
    page_url='https://donor-name2.com/url',
    anchor='anchor_text2',
    link_url='https://project-name2.com/url/',
)


def test_can_create_page_url_domains(session_in_memory, repo_in_memory):
    """test page_url_domains (donors) can be created from just created links"""
    repo = repo_in_memory
    session = session_in_memory

    link_1 = repo.create(LinkModel, link_1_serializer)
    recreate_domains(session, link_1)

    link_2 = repo.create(LinkModel, link_2_serializer)
    recreate_domains(session, link_2)

    pu_domains = repo.get_all(PageUrlDomainModel)
    assert pu_domains == [link_1.page_url_domain, link_2.page_url_domain]


def test_page_url_domain_is_filtered_by_tags(session_in_memory, repo_in_memory):
    """test
    - tags can be assigned to page_url_domains
    - page_url_domains can be filtered by tags
    """
    repo = repo_in_memory
    session = session_in_memory

    link_1 = repo.create(LinkModel, link_1_serializer)
    recreate_domains(session, link_1)

    link_2 = repo.create(LinkModel, link_2_serializer)
    recreate_domains(session, link_2)

    pud_1 = repo.get(LinkModel, **link_1_serializer.dict()).page_url_domain
    pud_2 = repo.get(LinkModel, **link_2_serializer.dict()).page_url_domain

    tag_language_1 = repo.create(TagModel, TagCreateSerializer(name='en', ref_property='language'))
    tag_language_2 = repo.create(TagModel, TagCreateSerializer(name='ru', ref_property='language'))
    tag_country_1 = repo.create(TagModel, TagCreateSerializer(name='eng', ref_property='country'))
    tag_country_2 = repo.create(TagModel, TagCreateSerializer(name='rus', ref_property='country'))

    pud_1.tags = [tag_language_1, tag_country_1]
    pud_2.tags = [tag_language_2, tag_country_2]
    session.commit()

    pudomain_params = pudomain_params_dependency()
    pudomain_params['language_tags_id'] = list(map(str, [tag_language_1.id]))
    pudomain_params['country_tags_id'] = []

    pudomains_query = session.query(PageUrlDomainModel)
    pudomains_query = filter_query_by_model_params_pudomain(pudomains_query, pudomain_params)
    total_domains_count = pudomains_query.count()
    pudomains = pudomains_query.all()
    assert total_domains_count == 1
    assert pudomains == [pud_1]

    pudomain_params = pudomain_params_dependency()
    pudomain_params['language_tags_id'] = []
    pudomain_params['country_tags_id'] = list(map(str, [tag_country_2.id]))

    pudomains_query = session.query(PageUrlDomainModel)
    pudomains_query = filter_query_by_model_params_pudomain(pudomains_query, pudomain_params)
    total_domains_count = pudomains_query.count()
    pudomains = pudomains_query.all()
    assert total_domains_count == 1
    assert pudomains == [pud_2]
