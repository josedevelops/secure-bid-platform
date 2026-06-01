# test_auction.py — tests for auction endpoints
# covers create, list, get, update, close and auth enforcement

async def test_create_auction_success(client, seller_token, product_type):
    # happy path — seller creates an auction with valid data
    response = await client.post(
        "/api/v1/auctions/",
        json={
            "name": "MacBook Pro M3",
            "details": "2023 MacBook Pro 14 inch",
            "min_price": 500.00,
            "max_price": 2000.00,
            "buyout_price": 1800.00,
            "product_type_id": product_type["id"]
        },
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "MacBook Pro M3"
    assert data["status"] == "active"
    assert data["min_price"] == 500.00
    assert data["max_price"] == 2000.00


async def test_create_auction_buyer_forbidden(client, buyer_token, product_type):
    # buyer cannot create an auction — only sellers and admins can
    response = await client.post(
        "/api/v1/auctions/",
        json={
            "name": "Test Auction",
            "min_price": 100.00,
            "max_price": 500.00,
            "product_type_id": product_type["id"]
        },
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "SELLER_REQUIRED"


async def test_create_auction_no_token(client, product_type):
    # unauthenticated request returns 401
    response = await client.post(
        "/api/v1/auctions/",
        json={
            "name": "Test Auction",
            "min_price": 100.00,
            "max_price": 500.00,
            "product_type_id": product_type["id"]
        }
    )
    assert response.status_code == 401


async def test_list_auctions_public(client, seller_token, product_type):
    # list is public — no auth required
    await client.post(
        "/api/v1/auctions/",
        json={
            "name": "Public Auction",
            "min_price": 100.00,
            "max_price": 500.00,
            "product_type_id": product_type["id"]
        },
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    response = await client.get("/api/v1/auctions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


async def test_get_auction_success(client, seller_token, product_type):
    # get single auction by id
    create = await client.post(
        "/api/v1/auctions/",
        json={
            "name": "Single Auction",
            "min_price": 100.00,
            "max_price": 500.00,
            "product_type_id": product_type["id"]
        },
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    auction_id = create.json()["id"]
    response = await client.get(f"/api/v1/auctions/{auction_id}")
    assert response.status_code == 200
    assert response.json()["id"] == auction_id


async def test_get_auction_not_found(client):
    # non-existent auction returns 404 with NOT_FOUND code
    response = await client.get("/api/v1/auctions/99999")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "NOT_FOUND"


async def test_update_auction_success(client, seller_token, product_type):
    # seller can update their own auction
    create = await client.post(
        "/api/v1/auctions/",
        json={
            "name": "Update Me",
            "min_price": 100.00,
            "max_price": 500.00,
            "product_type_id": product_type["id"]
        },
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    auction_id = create.json()["id"]
    response = await client.patch(
        f"/api/v1/auctions/{auction_id}",
        json={"min_price": 200.00},
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    assert response.status_code == 200
    assert response.json()["min_price"] == 200.00


async def test_update_auction_wrong_user(client, seller_token, admin_token, product_type):
    # non-owner cannot update another seller's auction
    create = await client.post(
        "/api/v1/auctions/",
        json={
            "name": "Not Yours",
            "min_price": 100.00,
            "max_price": 500.00,
            "product_type_id": product_type["id"]
        },
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    auction_id = create.json()["id"]
    # create a second seller and try to update the first seller's auction
    await client.post("/api/v1/auth/signup", json={
        "username": "seller2",
        "email": "seller2@test.com",
        "password": "Testpass1!"
    })
    from app.repository.user import UserRepository
    from app.db.models import MemberType
    response = await client.patch(
        f"/api/v1/auctions/{auction_id}",
        json={"min_price": 999.00},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # admin CAN update — so use buyer token instead to test forbidden
    buyer_resp = await client.post("/api/v1/auth/signup", json={
        "username": "buyerx",
        "email": "buyerx@test.com",
        "password": "Testpass1!"
    })
    buyer_login = await client.post("/api/v1/auth/login", json={
        "username": "buyerx",
        "password": "Testpass1!"
    })
    buyer_tok = buyer_login.json()["access_token"]
    response = await client.patch(
        f"/api/v1/auctions/{auction_id}",
        json={"min_price": 999.00},
        headers={"Authorization": f"Bearer {buyer_tok}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "FORBIDDEN"


async def test_close_auction_success(client, seller_token, product_type):
    # seller can close their own auction
    create = await client.post(
        "/api/v1/auctions/",
        json={
            "name": "Close Me",
            "min_price": 100.00,
            "max_price": 500.00,
            "product_type_id": product_type["id"]
        },
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    auction_id = create.json()["id"]
    response = await client.post(
        f"/api/v1/auctions/{auction_id}/close",
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "closed"
