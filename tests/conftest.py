import pytest

SAMPLE_LOGIN_HTML = """\
<html>
<body>
<form id="loginForm" action="/qisserver/rds?state=user&amp;type=1" method="post">
  <input type="hidden" name="javax.faces.ViewState" value="abc123viewstate" />
  <input type="hidden" name="csrf_token" value="xyz789csrf" />
  <div>
    <label for="asdf">Username</label>
    <input type="text" id="asdf" name="asdf" />
  </div>
  <div>
    <label for="fdsauhi">Password</label>
    <input type="password" id="fdsauhi" name="fdsauhi" />
  </div>
  <input type="submit" name="loginForm:login" value="Login" />
</form>
</body>
</html>
"""

SAMPLE_LOGIN_HTML_NO_FORM = """\
<html><body><p>No form here</p></body></html>
"""

SAMPLE_LOGIN_HTML_NO_PASSWORD = """\
<html>
<body>
<form id="loginForm" action="/login" method="post">
  <input type="text" name="username" />
</form>
</body>
</html>
"""

SAMPLE_GRADES_PAGE_WITH_LINK = """\
<html>
<body>
<a href="/notenspiegel?detail=true">Notenspiegel anzeigen</a>
</body>
</html>
"""

SAMPLE_GRADES_TABLE = """\
<html>
<body>
<table>
  <tr>
    <th>Nr</th><th>Name</th><th>Note</th><th>Status</th><th>LP</th>
  </tr>
  <tr>
    <td>1</td>
    <td>INF-001/\nEinführung in die Informatik</td>
    <td>1,3</td>
    <td>bestanden</td>
    <td>6,0</td>
  </tr>
  <tr>
    <td>2</td>
    <td>INF-002/\nDatenbanken</td>
    <td>2,0</td>
    <td>bestanden</td>
    <td>9,0</td>
  </tr>
  <tr>
    <td>3</td>
    <td>INF-003/\nSoftwaretechnik</td>
    <td></td>
    <td>angemeldet</td>
    <td>6,0</td>
  </tr>
</table>
</body>
</html>
"""

SAMPLE_GRADES_TABLE_EMPTY = """\
<html>
<body>
<table>
  <tr>
    <th>Nr</th><th>Name</th><th>Note</th><th>Status</th><th>LP</th>
  </tr>
</table>
</body>
</html>
"""

SAMPLE_GRADES_TABLE_NO_TABLE = """\
<html><body><p>No grades available</p></body></html>
"""


@pytest.fixture
def sample_grades():
    return [
        {"name": "Einführung in die Informatik", "grade": "1,3", "credits": "6,0"},
        {"name": "Datenbanken", "grade": "2,0", "credits": "9,0"},
    ]


@pytest.fixture
def sample_grades_with_new():
    return [
        {"name": "Einführung in die Informatik", "grade": "1,3", "credits": "6,0"},
        {"name": "Datenbanken", "grade": "2,0", "credits": "9,0"},
        {"name": "Softwaretechnik", "grade": "1,7", "credits": "6,0"},
    ]
