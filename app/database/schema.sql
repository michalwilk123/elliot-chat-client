
CREATE TABLE USERS(
    login VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_key TEXT NOT NULL,
    signed_pre_key TEXT NOT NULL
);

CREATE TABLE CONTACTS(
    owner VARCHAR(255) NOT NULL,
    login VARCHAR(255) NOT NULL,
    shared_x3dh_key TEXT,

    dh_ratchet TEXT,
    send_ratchet TEXT,
    recv_ratchet TEXT,
    root_ratchet TEXT,

    current_turn INTEGER,
    FOREIGN KEY(login) REFERENCES USERS(login),
    PRIMARY KEY (owner, login)
);

CREATE TABLE ONE_TIME_KEYS(
    key_index INTEGER NOT NULL,
    owner VARCHAR(255) NOT NULL,
    key TEXT,
    FOREIGN KEY(owner) REFERENCES USERS(login),
    PRIMARY KEY (key_index, owner)
);