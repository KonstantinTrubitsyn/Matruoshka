CREATE TABLE users
(
    id        SERIAL PRIMARY KEY,
    email     VARCHAR(255) UNIQUE NOT NULL,
    password  VARCHAR(255)        NOT NULL,
    full_name VARCHAR(255)        NOT NULL,
    address   TEXT                NOT NULL
);

CREATE TABLE items
(
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(255)   NOT NULL,
    price       DECIMAL(10, 2) NOT NULL,
    year        INT            NOT NULL,
    description TEXT           NOT NULL,
    location    TEXT           NOT NULL,
    user_id     INT            NOT NULL REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE ratings
(
    id      SERIAL PRIMARY KEY,
    item_id INT                               NOT NULL REFERENCES items (id) ON DELETE CASCADE,
    user_id INT                               NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    stars   INT CHECK (stars BETWEEN 1 AND 5) NOT NULL,
    UNIQUE (item_id, user_id)
);