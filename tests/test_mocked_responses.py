from requests_mock import ANY


def test_get_all_lists(mock_client, mocker, mock_response):
    with mocker:
        mocker.get(ANY, status_code=200, json=mock_response)
        response = mock_client.get_all_lists()

    assert isinstance(response, list)
    assert len(response) == 2
    assert response[0].name == "Test List"
    assert response[1].name == "CreateTest"


def test_get_single_list(mock_client, mocker, mock_response):
    with mocker:
        mocker.get(ANY, status_code=200, json=mock_response)
        response = mock_client.get_list("bffba6ef-b85a-4b26-932b-00875b74ca2e")

    assert response.name == "Test List"
