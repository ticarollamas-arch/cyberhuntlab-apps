const fs = require('fs');
app.get('/file', (req, res) => {
  const name = req.query.path;
  const data = fs.readFileSync('/srv/' + name);
  res.send(data);
});
