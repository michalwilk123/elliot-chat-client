
CREATE TABLE USERS(
    login VARCHAR(255) PRIMARY KEY,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_key TEXT NOT NULL,
    signed_pre_key TEXT NOT NULL
);

CREATE TABLE CONTACTS(
    owner VARCHAR(255) NOT NULL,
    login VARCHAR(255) NOT NULL,

    shared_x3dh_key TEXT NOT NULL,
    dh_ratchet TEXT,
    send_ratchet TEXT,
    recv_ratchet TEXT,
    root_ratchet TEXT,

    public_id_key TEXT NOT NULL,
    public_signed_pre_key TEXT,
    my_ephemeral_key TEXT,
    contact_ephemeral_key TEXT,
    my_otk_key TEXT,
    contact_otk_key TEXT,

    my_turn INTEGER,
    approved_user INTEGER,
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