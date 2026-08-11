'''
P1: coverage del 30% aprox. Los tests solo van a testear las corrutinas fetch_model y fetch_all_robust

P2: se queda atorado en el assert que falla
'''

import httpx
import pytest
import respx

from robust_client import BASE_URL, MODEL_IDS, fetch_all_robust, fetch_model


@respx.mock
async def test_happy_model(client) -> None:
    respx.get(f"{BASE_URL}/models/1").mock(
        return_value=httpx.Response(200, json={"id":1, 
                                               "name": "claude-fable-5", 
                                               "provider": "anthropic", 
                                               "max_tokens": 64000})
    )

    result = await fetch_model(client,1)
    assert result == {"id":1, 
                    "name": "claude-fable-5", 
                    "provider": "anthropic", 
                    "max_tokens": 64000}

@respx.mock
@pytest.mark.parametrize("status", [401,403,500])
async def test_param_error_status(status: int, client) -> None:
    respx.get(f"{BASE_URL}/models/1").mock(
        return_value=httpx.Response(status)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await fetch_model(client, 1)


@respx.mock
async def test_timeout_models(client) -> None:
    respx.get(f"{BASE_URL}/models/1").mock(
        side_effect=httpx.ReadTimeout("too slow")
    )
    with pytest.raises(httpx.TimeoutException):
        await fetch_model(client, 1)


@respx.mock
async def test_mixed_case() -> None:
    for model_id in MODEL_IDS:
        if model_id == 3:
            respx.get(f"{BASE_URL}/models/{model_id}").mock(
            return_value=httpx.Response(500)
            )

        elif model_id == 7:
            respx.get(f"{BASE_URL}/models/{model_id}").mock(
                side_effect=httpx.ReadTimeout("too slow")
            )

        else:
            respx.get(f"{BASE_URL}/models/{model_id}").mock(
                return_value=httpx.Response(200,
                                json={"id":model_id, 
                                        "name": "claude-fable-5", 
                                        "provider": "anthropic", 
                                        "max_tokens": 64000})
            )



    results = await fetch_all_robust()
    for model_id in MODEL_IDS:
        if model_id == 3:
            assert isinstance(results[model_id], httpx.HTTPStatusError)

        elif model_id == 7:
            assert isinstance(results[model_id], httpx.TimeoutException)

        else:
            assert results[model_id] == {"id":model_id, 
                                        "name": "claude-fable-5", 
                                        "provider": "anthropic", 
                                        "max_tokens": 64000}



@respx.mock
async def test_spy_models(client) -> None:
    route = respx.get(f"{BASE_URL}/models/1").mock(
            return_value=httpx.Response(200, json={"id":1, 
                                                   "name": "claude-fable-5", 
                                                   "provider": "anthropic", 
                                                   "max_tokens": 64000})
        )

    await fetch_model(client, 1)

    assert route.called
    assert route.call_count == 1
    assert route.calls.last.request.url.path == "/models/1"