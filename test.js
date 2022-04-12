const { google } = require('googleapis');
const Photos = require('googlephotos');
const input = require('input')
const ora = require('ora')
const { readFileSync, writeFileSync, existsSync, mkdirSync, createWriteStream } = require('fs')
const { join } = require('path')
const https = require('https'); // or 'https' for https:// URLs

const TOKEN_FILE = '.token'
const DOWNLOAD_DIR = 'downloads'

const getToken = async () => {
  if (existsSync(TOKEN_FILE)) {
    const tokens = JSON.parse(readFileSync(TOKEN_FILE))
    if (tokens.expiry_date > new Date().getTime()) {
      return tokens.access_token
    }
  }

  const server = () => {
    return new Promise((resolve, reject) => {
      var express = require('express');
      var app = express();

      // respond with "hello world" when a GET request is made to the homepage
      app.get('/', function(req, res) {
        res.send('<script>window.close()</script>');
        server.close()
        resolve(req.query)
      });

      let server = app.listen(5555)
    })

  }
  const a = require('./asd.json').installed

  const { client_id, client_secret } = a

  const oauth2Client = new google.auth.OAuth2(client_id, client_secret, 'http://localhost:5555')

  const scopes = [Photos.Scopes.READ_AND_APPEND];

  const url = oauth2Client.generateAuthUrl({
    // 'online' (default) or 'offline' (gets refresh_token)
    access_type: 'offline',
    scope: scopes,
  });

  console.log(url)
  const res = await server()
  const { code } = res

  const { tokens } = await oauth2Client.getToken(code);

  writeFileSync(TOKEN_FILE, JSON.stringify(tokens))

  return tokens.access_token
}
const download = (path, url) => new Promise( (resolve, reject) => {

  const file = createWriteStream(path);
  const request = https.get(url, function(response) {
    response.pipe(file);

    file.on("finish", () => {
      file.close();
      resolve(path);
    });
  });

})
const filePath = (name) => join(DOWNLOAD_DIR, name)

async function main() {

  if (!existsSync(DOWNLOAD_DIR)) {
    mkdirSync(DOWNLOAD_DIR)
  }

  const token = await getToken()
  let photos = new Photos(token);

  const spinner = ora('Leyendo fotos y videos').start();

  let nextPageToken = undefined
  let count = 0

  do {
    const { mediaItems, nextPageToken: newPageToken } = await photos.mediaItems.list(10, nextPageToken)
    for ( let media of mediaItems ){
      let path = filePath( media.filename )
      if( !existsSync( path ) )  {
        await download( path, media.baseUrl )
      }
      count ++
      spinner.text = `Leyendo: ${count} recursos cargados`;
    }
    nextPageToken = newPageToken
  } while (nextPageToken !== undefined)

  spinner.succeed('Todos los recursos descargados')

}
main()
