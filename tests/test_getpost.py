from unittest import TestCase
from mock import Mock
from blogger import EasyBlogger
from apiclient.errors import HttpError


try:
    content = bytes("", "UTF-8")
except TypeError:
    content = bytes("")


class GetPostsTests(TestCase):

    def setUp(self):
        self.blogger = EasyBlogger("id", "secret", "1234")
        self.blogger.service = Mock()
        self.posts = self.blogger.service.posts.return_value

    def tearDown(self):
        self.blogger = None

    def test_should_get_blog_by_labels(self):
        # Arrange
        request = self.posts.list.return_value
        request.execute.return_value = {"items": []}
        self.posts.list_next.return_value = None

        # act
        for x in self.blogger.getPosts(labels="abc", maxResults=4):
            pass
        # assert
        self.posts.list.assert_called_with(
            blogId="1234",
            labels="abc",
            maxResults=4)

    def test_should_default_search_by_labels(self):
        req = self.posts.list.return_value
        req.execute.return_value = {"items": []}
        self.posts.list_next.return_value = None

        for x in self.blogger.getPosts():
            pass

        self.posts.list.assert_called_with(
            blogId=self.blogger.blogId,
            labels="",
            maxResults=None)
        req.execute.assert_called()

    def test_should_use_search_when_query_is_provided(self):
        req = self.posts.search.return_value
        req.execute.return_value = {"items": []}
        self.posts.list_next.return_value = None

        for x in self.blogger.getPosts(query="test"):
            pass

        self.posts.search.assert_called_with(blogId=self.blogger.blogId,
                                             q="test")
        req.execute.assert_called()

    def test_should_get_blog_by_id(self):
        req = self.posts.get.return_value
        item = {"id": 23234}
        req.execute.return_value = item

        post = [p for p in self.blogger.getPosts(postId="234")]

        self.posts.get.assert_called_with(
            blogId="1234", postId="234", view="AUTHOR")
        req.execute.assert_called()
        assert len(post) == 1
        assert post[0] == item

    def test_should_get_blog_by_url(self):
        req = self.posts.getByPath.return_value
        item = {"id": 23234}
        req.execute.return_value = item

        post = [x for x in self
                .blogger
                .getPosts(url="https://somedomain.com/some/path.html")]

        self.posts.getByPath.assert_called_with(
            blogId="1234", path="/some/path.html")
        req.execute.assert_called()
        assert len(post) == 1
        assert post[0] == item

    def test_should_return_empty_array_when_id_not_found(self):
        req = self.posts.get.return_value
        resp = Mock()
        resp.status = 404
        req.execute.side_effect = HttpError(resp, content)

        post = [x for x in self.blogger.getPosts(postId="234")]

        self.posts.get.assert_called_with(
            blogId="1234", postId="234", view="AUTHOR")
        req.execute.assert_called()
        assert len(post) == 0

    def test_should_rethrow_exception_other_than_404(self):
        req = self.posts.get.return_value
        resp = Mock()
        resp.status = 401
        req.execute.side_effect = HttpError(resp, content)

        with self.assertRaises(HttpError):
            for x in self.blogger.getPosts(postId="234"):
                pass

        self.posts.get.assert_called_with(
            blogId="1234", postId="234", view="AUTHOR")
        req.execute.assert_called()
