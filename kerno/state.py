"""Classes that store state."""

from abc import ABCMeta
from typing import Any, Dict, List  # noqa


class UIMessage:
    """Represents a message to be displayed to the user in the UI."""

    KINDS = ["danger", "warning", "info", "success"]

    def __init__(
        self, title: str="", kind: str="danger", plain: str="", html: str="",
    ) -> None:
        """Constructor.

        ``kind`` must be one of ("danger", "warning", "info", "success").
        """
        args_are_valid = (plain and not html) or (html and not plain)
        assert args_are_valid
        if kind == "error":
            kind = "danger"
        assert kind in self.KINDS, 'Unknown kind of message: "{0}". ' \
            "Possible kinds are {1}".format(kind, self.KINDS)
        self.kind = kind
        self.title = title
        self.plain = plain
        self.html = html

    def __repr__(self) -> str:
        return '<{} "{}">'.format(self.__class__.__name__, self.title)

    def to_dict(self) -> Dict:  # TODO Remove
        """Convert instance to a dictionary, usually for JSON output."""
        return self.__dict__.copy()


class Returnable(metaclass=ABCMeta):
    """Base class for Rezulto and for MalbonaRezulto.

    Returnable is the base class for what Actions should return. It contains:

    - messages: Grave UI messages.
    - toasts: UI messages that disappear automatically after a while.
    - debug: A dict with information that is not displayed to the end user.
    - redirect: URL or screen to redirect to.

    Subclasses overload the ``status_int`` and ``kind`` static variables.
    """

    kind = "danger"
    status_int = 500  # HTTP response code indicating server bug/failure

    def __init__(self) -> None:
        """Construct."""
        self.messages = []  # type: List[UIMessage]
        self.toasts = []    # type: List[UIMessage]
        self.debug = {}     # type: Dict[str, Any]
        self.redirect = None

    def __repr__(self) -> str:
        return "<{} status: {}>".format(
            self.__class__.__name__, self.status_int)

    def to_dict(self) -> Dict[str, Any]:  # TODO Remove
        """Convert this to a dictionary, usually for JSON output."""
        return dict(
            messages=[m.to_dict() for m in self.messages],
            toasts=[m.to_dict() for m in self.toasts],
            debug=self.debug,
            redirect=self.redirect)

    def add_message(
        self, title: str="", kind: str="", plain: str="", html: str="",
    ):
        """Add to the grave messages to be displayed to the user on the UI."""
        msg = UIMessage(
            title=title, kind=kind or self.kind, plain=plain, html=html)
        self.messages.append(msg)
        return msg

    def add_toast(
        self, title: str="", kind: str="", plain: str="", html: str="",
    ) -> UIMessage:
        """Add to the quick messages to be displayed to the user on the UI."""
        msg = UIMessage(
            title=title, kind=kind or self.kind, plain=plain, html=html)
        self.toasts.append(msg)
        return msg


class Rezulto(Returnable):
    """Well-organized successful response object.

    When your action succeeds you should return a Rezulto.
    Unsuccessful operations raise MalbonaRezulto instead.
    """

    kind = "success"
    status_int = 200  # HTTP response code indicating success

    def __init__(self) -> None:
        """Constructor."""
        super().__init__()
        self.payload = {}  # type: Dict[str, Any]

    def to_dict(self):  # TODO Remove
        """Convert instance to a dictionary, usually for JSON output."""
        adict = super().to_dict()
        adict["payload"] = self.payload
        return adict


class MalbonaRezulto(Returnable, Exception):
    """Base class for exceptions raised by actions."""

    kind = "danger"
    status_int = 400  # HTTP response code indicating invalid request

    def __init__(self, status_int: int=400, title: str="", plain: str="",
                 html: str="", kind: str="danger") -> None:
        """Constructor."""
        Returnable.__init__(self)
        self.status_int = status_int
        if title or plain or html:
            self.add_message(
                title=title, kind=kind, plain=plain, html=html)
