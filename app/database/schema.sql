
CREATE TABLE USERS(
    login VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_key BLOB,
    signed_pre_key BLOB
);

CREATE TABLE CONTACTS(
    owner VARCHAR(255) NOT NULL,
    login VARCHAR(255) NOT NULL,
    shared_x3dh_key BLOB,
    send_ratchet BLOB,
    recv_ratchet BLOB,
    DH_ratchet BLOB,
    FOREIGN KEY(login) REFERENCES USERS(login),
    PRIMARY KEY (owner, login)
);