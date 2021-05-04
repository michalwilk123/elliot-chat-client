


def test_add_new_contact(mocker):
    """
    Test adding new contact to the database 
    (without full handshake). But now with mocked 
    server
    """
    assert False


def test_continue_contact_add(mocker):
    """
    Scenario: 
        user A adds user B and quits the app

    He wants for the next app start to be 
    already connected with user B

    So we need 2 app controllers
    """
    assert False

def test_approve_contact_add(mocker):
    """
    Scenario:
        User A added user B as a new contact.
        At this time B had the app closed.
        He now starts his app normally.

        He now wants to have user A
        in his contact list after startup.

        In the background we do all the initial
        ratchet rotations and handshake 
        shenanigans
    """
    assert False
