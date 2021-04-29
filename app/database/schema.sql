
CREATE TABLE USERS(
    login VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_key TEXT,
    signed_pre_key TEXT
);

CREATE TABLE CONTACTS(
    owner VARCHAR(255) NOT NULL,
    login VARCHAR(255) NOT NULL,
    shared_x3dh_key TEXT,
    send_ratchet TEXT,
    recv_ratchet TEXT,
    send_ratchet_step INTEGER DEFAULT 0,
    recv_ratchet_step INTEGER DEFAULT 0,
    FOREIGN KEY(login) REFERENCES USERS(login),
    PRIMARY KEY (owner, login)
);