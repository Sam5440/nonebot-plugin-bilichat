# Edge GPT 0.8.2
from __future__ import annotations

import asyncio
import json
import os
import random
import ssl
import sys
import uuid
from enum import Enum
from typing import Literal, Optional, Union

import aiohttp
import certifi
import httpx

from ..model.exception import BaseBingChatException

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


DELIMITER = "\x1e"

# Generate random IP between range 13.104.0.0/14
FORWARDED_IP = f"13.{random.randint(104, 107)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "sec-ch-ua": '"Not_A Brand";v="99", "Microsoft Edge";v="110", "Chromium";v="110"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"109.0.1518.78"',
    "sec-ch-ua-full-version-list": '"Chromium";v="110.0.5481.192", "Not A(Brand";v="24.0.0.0", "Microsoft Edge";v="110.0.1587.69"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": "",
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"15.0.0"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-ms-client-request-id": str(uuid.uuid4()),
    "x-ms-useragent": "azsdk-js-api-client-factory/1.0.0-beta.1 core-rest-pipeline/1.10.0 OS/Win32",
    "Referer": "https://www.bing.com/search?q=Bing+AI&showconv=1&FORM=hpcodx",
    "Referrer-Policy": "origin-when-cross-origin",
    "x-forwarded-for": FORWARDED_IP,
}

HEADERS_INIT_CONVER = {
    "authority": "edgeservices.bing.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"110.0.1587.69"',
    "sec-ch-ua-full-version-list": '"Chromium";v="110.0.5481.192", "Not A(Brand";v="24.0.0.0", "Microsoft Edge";v="110.0.1587.69"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"15.0.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69",
    "x-edge-shopping-flag": "1",
    "x-forwarded-for": FORWARDED_IP,
}


class NotAllowedToAccess(BaseBingChatException):
    pass


class LocationHint(Enum):
    USA = {
        "locale": "en-US",
        "LocationHint": [
            {
                "country": "United States",
                "state": "California",
                "city": "Los Angeles",
                "timezoneoffset": 8,
                "countryConfidence": 8,
                "Center": {
                    "Latitude": 34.0536909,
                    "Longitude": -118.242766,
                },
                "RegionType": 2,
                "SourceType": 1,
            },
        ],
    }
    CHINA = {
        "locale": "zh-CN",
        "LocationHint": [
            {
                "country": "China",
                "state": "",
                "city": "Beijing",
                "timezoneoffset": 8,
                "countryConfidence": 8,
                "Center": {
                    "Latitude": 39.9042,
                    "Longitude": 116.4074,
                },
                "RegionType": 2,
                "SourceType": 1,
            },
        ],
    }
    EU = {
        "locale": "en-IE",
        "LocationHint": [
            {
                "country": "Norway",
                "state": "",
                "city": "Oslo",
                "timezoneoffset": 1,
                "countryConfidence": 8,
                "Center": {
                    "Latitude": 59.9139,
                    "Longitude": 10.7522,
                },
                "RegionType": 2,
                "SourceType": 1,
            },
        ],
    }
    UK = {
        "locale": "en-GB",
        "LocationHint": [
            {
                "country": "United Kingdom",
                "state": "",
                "city": "London",
                "timezoneoffset": 0,
                "countryConfidence": 8,
                "Center": {
                    "Latitude": 51.5074,
                    "Longitude": -0.1278,
                },
                "RegionType": 2,
                "SourceType": 1,
            },
        ],
    }


LOCATION_HINT_TYPES = Optional[Union[LocationHint, Literal["USA", "CHINA", "EU", "UK"]]]


class ConversationStyle(Enum):
    creative = [
        "nlu_direct_response_filter",
        "deepleo",
        "disable_emoji_spoken_text",
        "responsible_ai_policy_235",
        "enablemm",
        "h3imaginative",
        "cachewriteext",
        "e2ecachewrite",
        "nodlcpcwrite",
        "nointernalsugg",
        "saharasugg",
        "enablenewsfc",
        "dv3sugg",
        "clgalileo",
        "gencontentv3",
        "nojbfedge",
    ]
    balanced = [
        "nlu_direct_response_filter",
        "deepleo",
        "disable_emoji_spoken_text",
        "responsible_ai_policy_235",
        "enablemm",
        "harmonyv3",
        "cachewriteext",
        "e2ecachewrite",
        "nodlcpcwrite",
        "nointernalsugg",
        "saharasugg",
        "enablenewsfc",
        "dv3sugg",
        "nojbfedge",
    ]
    precise = [
        "nlu_direct_response_filter",
        "deepleo",
        "disable_emoji_spoken_text",
        "responsible_ai_policy_235",
        "enablemm",
        "h3precise",
        "cachewriteext",
        "e2ecachewrite",
        "nodlcpcwrite",
        "nointernalsugg",
        "saharasugg",
        "enablenewsfc",
        "dv3sugg",
        "clgalileo",
        "gencontentv3",
        "nojbfedge",
    ]


CONVERSATION_STYLE_TYPE = Optional[Union[ConversationStyle, Literal["creative", "balanced", "precise"]]]

LOCALE = "en-US"


def get_location_hint_from_locale(locale: str) -> Union[dict, None]:
    locale = locale.lower()
    if locale == "en-gb":
        hint = LocationHint.UK.value
    elif locale == "en-ie":
        hint = LocationHint.EU.value
    # elif locale == "zh-cn":
    #     hint = LocationHint.CHINA.value
    else:
        hint = LocationHint.USA.value
    return hint.get("LocationHint")


def _append_identifier(msg: dict) -> str:
    # Convert dict to json string
    return json.dumps(msg, ensure_ascii=False) + DELIMITER


def _get_ran_hex(length: int = 32) -> str:
    return "".join(random.choice("0123456789abcdef") for _ in range(length))


class _ChatHubRequest:
    def __init__(
        self,
        conversation_signature: str,
        client_id: str,
        conversation_id: str,
        invocation_id: int = 0,
    ) -> None:
        self.struct: dict = {}

        self.client_id: str = client_id
        self.conversation_id: str = conversation_id
        self.conversation_signature: str = conversation_signature
        self.invocation_id: int = invocation_id

    def update(
        self,
        prompt: str,
        conversation_style: CONVERSATION_STYLE_TYPE,
        options: list | None = None,
        webpage_context: str | None = None,
        search_result: bool = False,
        locale: str = LOCALE,
    ) -> None:
        if options is None:
            options = [
                "deepleo",
                "enable_debug_commands",
                "disable_emoji_spoken_text",
                "enablemm",
            ]
        if conversation_style:
            if not isinstance(conversation_style, ConversationStyle):
                conversation_style = getattr(ConversationStyle, conversation_style)
            options = conversation_style.value  # type: ignore
        self.struct = {
            "arguments": [
                {
                    "source": "cib",
                    "optionsSets": options,
                    "allowedMessageTypes": [
                        "Chat",
                        "Disengaged",
                        "AdsQuery",
                        "SemanticSerp",
                        "GenerateContentQuery",
                        "SearchQuery",
                        "ActionRequest",
                        "Context",
                        "Progress",
                        "AdsQuery",
                        "SemanticSerp",
                    ],
                    "sliceIds": [
                        "winmuid3tf",
                        "osbsdusgreccf",
                        "ttstmout",
                        "crchatrev",
                        "winlongmsgtf",
                        "ctrlworkpay",
                        "norespwtf",
                        "tempcacheread",
                        "temptacache",
                        "505scss0",
                        "508jbcars0",
                        "515enbotdets0",
                        "5082tsports",
                        "515vaoprvs",
                        "424dagslnv1s0",
                        "kcimgattcf",
                        "427startpms0",
                    ],
                    "traceId": _get_ran_hex(32),
                    "isStartOfSession": self.invocation_id == 0,
                    "message": {
                        "locale": locale,
                        "market": locale,
                        "region": locale[-2:],  # en-US -> US
                        "locationHints": get_location_hint_from_locale(locale),
                        "author": "user",
                        "inputMethod": "Keyboard",
                        "text": prompt,
                        "messageType": "Chat",
                    },
                    "conversationSignature": self.conversation_signature,
                    "participant": {
                        "id": self.client_id,
                    },
                    "conversationId": self.conversation_id,
                },
            ],
            "invocationId": str(self.invocation_id),
            "target": "chat",
            "type": 4,
        }
        if search_result:
            have_search_result = [
                "InternalSearchQuery",
                "InternalSearchResult",
                "InternalLoaderMessage",
                "RenderCardRequest",
            ]
            self.struct["arguments"][0]["allowedMessageTypes"] += have_search_result
        if webpage_context:
            self.struct["arguments"][0]["previousMessages"] = [
                {
                    "author": "user",
                    "description": webpage_context,
                    "contextType": "WebPage",
                    "messageType": "Context",
                    "messageId": "discover-web--page-ping-mriduna-----",
                },
            ]
        self.invocation_id += 1


class _Conversation:
    def __init__(
        self,
        proxy: str | None = None,
        async_mode: bool = False,
        cookies: list[dict] | None = None,
    ) -> None:
        if async_mode:
            return
        self.struct: dict = {
            "conversationId": None,
            "clientId": None,
            "conversationSignature": None,
            "result": {"value": "Success", "message": None},
        }
        self.proxy = proxy
        proxy = (
            proxy
            or os.environ.get("all_proxy")
            or os.environ.get("ALL_PROXY")
            or os.environ.get("https_proxy")
            or os.environ.get("HTTPS_PROXY")
            or None
        )
        if proxy is not None and proxy.startswith("socks5h://"):
            proxy = "socks5://" + proxy[len("socks5h://") :]
        self.session = httpx.Client(
            proxies=proxy,
            timeout=900,
            headers=HEADERS_INIT_CONVER,
        )
        if cookies:
            for cookie in cookies:
                self.session.cookies.set(cookie["name"], cookie["value"])
        # Send GET request
        response = self.session.get(
            url=os.environ.get("BING_PROXY_URL") or "https://edgeservices.bing.com/edgesvc/turing/conversation/create",
        )
        if response.status_code != 200:
            response = self.session.get(
                "https://edge.churchless.tech/edgesvc/turing/conversation/create",
            )
        if response.status_code != 200:
            print(f"Status code: {response.status_code}")
            print(response.text)
            print(response.url)
            raise BaseBingChatException("Authentication failed")
        try:
            self.struct = response.json()
        except (json.decoder.JSONDecodeError, NotAllowedToAccess) as exc:
            raise BaseBingChatException(
                "Authentication failed. You have not been accepted into the beta.",
            ) from exc
        if self.struct["result"]["value"] == "UnauthorizedRequest":
            raise NotAllowedToAccess(self.struct["result"]["message"])

    @staticmethod
    async def create(
        proxy: str | None = None,
        cookies: list[dict] | None = None,
    ) -> _Conversation:
        self = _Conversation(async_mode=True)
        self.struct = {
            "conversationId": None,
            "clientId": None,
            "conversationSignature": None,
            "result": {"value": "Success", "message": None},
        }
        self.proxy = proxy
        proxy = (
            proxy
            or os.environ.get("all_proxy")
            or os.environ.get("ALL_PROXY")
            or os.environ.get("https_proxy")
            or os.environ.get("HTTPS_PROXY")
            or None
        )
        if proxy is not None and proxy.startswith("socks5h://"):
            proxy = "socks5://" + proxy[len("socks5h://") :]
        transport = httpx.AsyncHTTPTransport(retries=900)
        # Convert cookie format to httpx format
        formatted_cookies = None
        if cookies:
            formatted_cookies = httpx.Cookies()
            for cookie in cookies:
                formatted_cookies.set(cookie["name"], cookie["value"])
        async with httpx.AsyncClient(
            proxies=proxy,
            timeout=30,
            headers=HEADERS_INIT_CONVER,
            transport=transport,
            cookies=formatted_cookies,
        ) as client:
            # Send GET request
            response = await client.get(
                url=os.environ.get("BING_PROXY_URL")
                or "https://edgeservices.bing.com/edgesvc/turing/conversation/create",
            )
            if response.status_code != 200:
                response = await client.get(
                    "https://edge.churchless.tech/edgesvc/turing/conversation/create",
                )
        if response.status_code != 200:
            print(f"Status code: {response.status_code}")
            print(response.text)
            print(response.url)
            raise BaseBingChatException("Authentication failed")
        try:
            self.struct = response.json()
        except (json.decoder.JSONDecodeError, NotAllowedToAccess) as exc:
            raise BaseBingChatException(
                "Authentication failed. You have not been accepted into the beta.",
            ) from exc
        if self.struct["result"]["value"] == "UnauthorizedRequest":
            raise NotAllowedToAccess(self.struct["result"]["message"])
        return self


class _ChatHub:
    def __init__(
        self,
        conversation: _Conversation,
        proxy: str | None = None,
        cookies: list[dict] | None = None,
    ) -> None:
        self.session: aiohttp.ClientSession = None  # type: ignore
        self.wss: aiohttp.ClientWebSocketResponse = None  # type: ignore
        self.request: _ChatHubRequest
        self.loop: bool
        self.task: asyncio.Task
        self.request = _ChatHubRequest(
            conversation_signature=conversation.struct["conversationSignature"],
            client_id=conversation.struct["clientId"],
            conversation_id=conversation.struct["conversationId"],
        )
        self.cookies = cookies
        self.proxy: str = proxy  # type: ignore

    async def ask_stream(
        self,
        prompt: str,
        wss_link: str,
        conversation_style: CONVERSATION_STYLE_TYPE = None,
        raw: bool = False,
        options: Optional[dict] = None,
        webpage_context: str | None = None,
        search_result: bool = False,
        locale: str = LOCALE,
    ):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=900))

        if self.wss and not self.wss.closed:
            await self.wss.close()
        # Check if websocket is closed
        self.wss = await self.session.ws_connect(
            wss_link,
            headers=HEADERS,
            ssl=ssl_context,
            proxy=self.proxy,
            autoping=False,
        )
        await self._initial_handshake()
        if self.request.invocation_id != 0:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://sydney.bing.com/sydney/UpdateConversation/",
                    json={
                        "messages": [
                            {
                                "author": "user",
                                "description": webpage_context,
                                "contextType": "WebPage",
                                "messageType": "Context",
                            },
                        ],
                        "conversationId": self.request.conversation_id,
                        "source": "cib",
                        "traceId": _get_ran_hex(32),
                        "participant": {"id": self.request.client_id},
                        "conversationSignature": self.request.conversation_signature,
                    },
                )
            if response.status_code != 200:
                print(f"Status code: {response.status_code}")
                print(response.text)
                print(response.url)
                raise BaseBingChatException("Update web page context failed")
        # Construct a ChatHub request
        self.request.update(
            prompt=prompt,
            conversation_style=conversation_style,
            options=options,  # type: ignore
            webpage_context=webpage_context,
            search_result=search_result,
            locale=locale,
        )
        # Send request
        await self.wss.send_str(_append_identifier(self.request.struct))
        final = False
        resp_txt = ""
        result_text = ""
        resp_txt_no_link = ""
        while not final:
            msg = await self.wss.receive(timeout=900)
            objects = msg.data.split(DELIMITER)
            for obj in objects:
                if obj is None or not obj:
                    continue
                response = json.loads(obj)
                if response.get("type") != 2 and raw:
                    yield False, response
                elif response.get("type") == 1 and response["arguments"][0].get(
                    "messages",
                ):
                    if response["arguments"][0]["messages"][0]["contentOrigin"] != "Apology":
                        resp_txt = result_text + response["arguments"][0]["messages"][0]["adaptiveCards"][0]["body"][
                            0
                        ].get("text", "")
                        resp_txt_no_link = result_text + response["arguments"][0]["messages"][0].get("text", "")
                        if response["arguments"][0]["messages"][0].get(
                            "messageType",
                        ):
                            resp_txt = (
                                resp_txt
                                + response["arguments"][0]["messages"][0]["adaptiveCards"][0]["body"][0]["inlines"][
                                    0
                                ].get("text")
                                + "\n"
                            )
                            result_text = (
                                result_text
                                + response["arguments"][0]["messages"][0]["adaptiveCards"][0]["body"][0]["inlines"][
                                    0
                                ].get("text")
                                + "\n"
                            )
                    yield False, resp_txt

                elif response.get("type") == 2:
                    if response["item"]["result"].get("error"):
                        await self.close()
                        raise BaseBingChatException(
                            f"{response['item']['result']['value']}: {response['item']['result']['message']}",
                        )

                    if response["item"]["messages"][-1]["contentOrigin"] == "Apology" and resp_txt:
                        response["item"]["messages"][-1]["text"] = resp_txt_no_link
                        response["item"]["messages"][-1]["adaptiveCards"][0]["body"][0]["text"] = resp_txt
                        print(
                            "Preserved the message from being deleted",
                            file=sys.stderr,
                        )
                    final = True
                    await self.close()
                    yield True, response

    async def _initial_handshake(self) -> None:
        await self.wss.send_str(_append_identifier({"protocol": "json", "version": 1}))
        await self.wss.receive(timeout=900)

    async def close(self) -> None:
        if self.wss and not self.wss.closed:
            await self.wss.close()
        if self.session and not self.session.closed:
            await self.session.close()


class Chatbot:
    """
    Combines everything to make it seamless
    """

    def __init__(
        self,
        proxy: str | None = None,
        cookies: list[dict] | None = None,
    ) -> None:
        self.proxy: str | None = proxy
        self.chat_hub: _ChatHub = _ChatHub(
            _Conversation(self.proxy, cookies=cookies),
            proxy=self.proxy,
            cookies=cookies,
        )

    @staticmethod
    async def create(
        proxy: str | None = None,
        cookies: list[dict] | None = None,
    ) -> Chatbot:
        self = Chatbot.__new__(Chatbot)
        self.proxy = proxy
        self.chat_hub = _ChatHub(
            await _Conversation.create(self.proxy, cookies=cookies),
            proxy=self.proxy,
            cookies=cookies,
        )
        return self

    async def ask(
        self,
        prompt: str,
        wss_link: str = "wss://sydney.bing.com/sydney/ChatHub",
        conversation_style: CONVERSATION_STYLE_TYPE = None,
        options: dict = None,  # type: ignore
        webpage_context: str | None = None,
        search_result: bool = False,
        locale: str = LOCALE,
    ) -> dict:
        """
        Ask a question to the bot
        """
        async for final, response in self.chat_hub.ask_stream(
            prompt=prompt,
            conversation_style=conversation_style,
            wss_link=wss_link,
            options=options,
            webpage_context=webpage_context,
            search_result=search_result,
            locale=locale,
        ):
            if final:
                return response  # type: ignore
        await self.chat_hub.wss.close()
        return {}

    async def ask_stream(
        self,
        prompt: str,
        wss_link: str = "wss://sydney.bing.com/sydney/ChatHub",
        conversation_style: CONVERSATION_STYLE_TYPE = None,
        raw: bool = False,
        options: dict = None,  # type: ignore
        webpage_context: str | None = None,
        search_result: bool = False,
        locale: str = LOCALE,
    ):
        """
        Ask a question to the bot
        """
        async for response in self.chat_hub.ask_stream(
            prompt=prompt,
            conversation_style=conversation_style,
            wss_link=wss_link,
            raw=raw,
            options=options,
            webpage_context=webpage_context,
            search_result=search_result,
            locale=locale,
        ):
            yield response

    async def close(self) -> None:
        """
        Close the connection
        """
        await self.chat_hub.close()

    async def reset(self) -> None:
        """
        Reset the conversation
        """
        await self.close()
        self.chat_hub = _ChatHub(
            await _Conversation.create(self.proxy, cookies=self.chat_hub.cookies),
            proxy=self.proxy,
            cookies=self.chat_hub.cookies,
        )
