# test_bid.py — tests for bid endpoints
# covers place bid, list bids, and business rule enforcement

async def test_place_bid_success(client, buyer_token, seller_token, product_type):
    # happy path — buyer places a valid bid on an active auction
    create = await client.post(
        "/api/v1/auctions/",
        json={
            "name": "Bid Target",
            "min_price": 100.00,
            "max_price": 500.00,
            "product_type_id": product_type["id"]
        },
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    auction_id = create.json()["id"]
    response = await client.post(
        "/api/v1/bids/",
        json={"auction_id": auction_id, "price": 150.00},
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["auction_id"] == auction_id
    assert data["price"] == 150.00


async def test_place_bid_no_token(client, seller_token, product_type):
    # unauthenticated request returns 401
    create = await client.post(
        "/api/v1/auctions/",
        json={
            "name": "No Token Auction",
            "min_price": 100.00,
            "max_price": 500.00,
            "product_type_id": product_type["id"]
        },
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    auction_id = create.json()["id"]
    response = await client.post(
        "/api/v1/bids/",
        json={"auction_id": auction_id, "price": 150.00}
    )
    assert response.status_code == 401


async def test_place_bid_auction_not_found(client, buyer_token):
    # bidding on non-existent auction returns 404
    response = await client.post(
        "/api/v1/bids/",
        json={"auction_id": 99999, "price": 150.00},
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "NOT_FOUND"


async def test_place_bid_on_closed_auction(client, buyer_token, seller_token, product_type):
    # cannot bid on a closed auction
    create = await client.post(
        "/api/v1/auctions/",
        json={
            "name": "Closed Auction",
            "min_price": 100.00,
            "max_price": 500.00,
            "product_type_id": product_type["id"]
        },
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    auction_id = create.json()["id"]
    # close the auction first
    await client.post(
        f"/api/v1/auctions/{auction_id}/close",
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    response = await client.post(
        "/api/v1/bids/",
        json={"auction_id": auction_id, "price": 150.00},
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "AUCTION_NOT_ACTIVE"


async def test_place_bid_self_bid(client, seller_token, product_type):
    # seller cannot bid on their own auction
    create = await client.post(
        "/api/v1/auctions/",
        json={
            "name": "Self Bid Auction",
            "min_price": 100.00,
            "max_price": 500.00,
            "product_type_id": product_type["id"]
        },
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    auction_id = create.json()["id"]
    response = await client.post(
        "/api/v1/bids/",
        json={"auction_id": auction_id, "price": 150.00},
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "SELF_BID"


async def test_place_bid_too_low(client, buyer_token, seller_token, product_type):
    # second bid must exceed the current highest bid
    create = await client.post(
        "/api/v1/auctions/",
        json={
            "name": "Outbid Auction",
            "min_price": 100.00,
            "max_price": 500.00,
            "product_type_id": product_type["id"]
        },
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    auction_id = create.json()["id"]
    # place first bid
    await client.post(
        "/api/v1/bids/",
        json={"auction_id": auction_id, "price": 200.00},
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    # place second bid lower than first — should fail
    response = await client.post(
        "/api/v1/bids/",
        json={"auction_id": auction_id, "price": 150.00},
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "BID_TOO_LOW"


async def test_list_bids_for_auction(client, buyer_token, seller_token, product_type):
    # list bids returns all bids for an auction
    create = await client.post(
        "/api/v1/auctions/",
        json={
            "name": "List Bids Auction",
            "min_price": 100.00,
            "max_price": 500.00,
            "product_type_id": product_type["id"]
        },
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    auction_id = create.json()["id"]
    await client.post(
        "/api/v1/bids/",
        json={"auction_id": auction_id, "price": 150.00},
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    response = await client.get(
        f"/api/v1/bids/auction/{auction_id}",
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["price"] == 150.00
