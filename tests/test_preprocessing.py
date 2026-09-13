import pytest
from src.preprocessing.reconstruct import (
    clean_tweet_text,
    reconstruct_conversations,
    filter_conversations_by_brand
)

def test_clean_tweet_text():
    raw = "Hello &amp; welcome &gt; test   whitespace   "
    cleaned = clean_tweet_text(raw)
    assert cleaned == "Hello & welcome > test whitespace"

def test_reconstruct_conversations():
    raw_tweets = [
        {
            "tweet_id": "1",
            "author_id": "1001",
            "inbound": True,
            "created_at": "Wed Oct 11 00:00:00 2017",
            "text": "@AppleSupport battery issue",
            "response_tweet_id": "2",
            "in_response_to_tweet_id": ""
        },
        {
            "tweet_id": "2",
            "author_id": "AppleSupport",
            "inbound": False,
            "created_at": "Wed Oct 11 00:05:00 2017",
            "text": "@1001 send us a DM",
            "response_tweet_id": "",
            "in_response_to_tweet_id": "1"
        }
    ]
    convs = reconstruct_conversations(raw_tweets)
    assert len(convs) == 1
    assert convs[0]["conversation_id"] == "1"
    assert convs[0]["brand"] == "AppleSupport"
    assert convs[0]["initial_customer_message"] == "@AppleSupport battery issue"

def test_filter_conversations_by_brand():
    convs = [
        {"conversation_id": "1", "brand": "AppleSupport", "all_brands": ["AppleSupport"]},
        {"conversation_id": "2", "brand": "SpotifyCares", "all_brands": ["SpotifyCares"]}
    ]
    apple_only = filter_conversations_by_brand(convs, "AppleSupport")
    assert len(apple_only) == 1
    assert apple_only[0]["conversation_id"] == "1"
