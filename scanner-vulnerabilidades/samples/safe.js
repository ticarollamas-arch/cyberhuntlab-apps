const path = require('path');
function read(req) {
  const p = path.basename(req.query.path);
  return fs.readFileSync(path.join('/srv', p));
}
