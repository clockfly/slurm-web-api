## Slurm Web UI
This is a project to provide a web interface to the Slurm cluster manager via
the slurm_rest_api project found here: [slurm_rest_api](https://github.com/rbogle/slurm-rest-api)

This project uses bootstrap and angularjs to provide a single-page dashboard app.

Warning: There are a few dirty dependencies on slurm and collectd to render this correctly.

#### Examples

Overview:
![alt text](https://cloud.githubusercontent.com/assets/7741121/24215694/c1375a3c-0ef6-11e7-92d9-eb094eb27bef.png "Overview")

Queue:
![alt text](https://cloud.githubusercontent.com/assets/7741121/24216518/af5e2da6-0ef9-11e7-82c9-a177c75adbb5.png "Queue")

History:
![alt text](https://cloud.githubusercontent.com/assets/7741121/24216566/f14c1052-0ef9-11e7-8e9d-c2ad72f88add.png "History")

Nodes:
![alt text](https://cloud.githubusercontent.com/assets/7741121/24216523/b69e4f2e-0ef9-11e7-9718-d9045c32d98d.png "Nodes")

Partitions:
![alt text](https://cloud.githubusercontent.com/assets/7741121/24216529/bd01d566-0ef9-11e7-8ecd-18fa75791c84.png "Partitions")

### Install and Dependencies
This project uses npm and bower to help with package management
You need to have those installed first.

1. Install NPM, slurm-rest-api

    Exercise left to developer.

    See [slurm_rest_api](https://github.com/rbogle/slurm-rest-api)
    for that repo's instructions.

2. Clone Repo
    ```
    git clone https://github.com/rbogle/slurm-web-api.git
    ```

3. Configure to match slurm-rest-api

    Modify `app/config.js` and set the Url's to match where you are hosting slurm-rest-api.
    
    `queueStatusUrl` can be pointed to any url that displays your slurm queue status.
    
    Note: if you are running slurm-rest-api and slurm-web-api on the same server, you may have to enable CORS on slurm-rest-api. See https://github.com/corydolphin/flask-cors for more information.

4. Run NPM, bower

    Run npm install to install the dev server and bower, then our package.json file should trigger bower to download javascript dependencies and place them in app/lib

    ```
      npm install

    ```

5. Testing and Development

    The project includes the spec for lite-server. You can start the server with

    ```
    npm start
    ```

    this will open the web app in your broswer on localhost:3000

### Deploy Notes
I deployed this to a subdirectory on an nginx server.

To get correct routing,urls,refresh I found the nginx config had to be like this:
```
location /<baseref>/ {
    alias <docrootpath>/;
    expires -1;
    add_header Pragma "no-cache";
    add_header Cache-Control "no-store, no-cache, must-revalidate, post-check=0, pre-check=0";
    try_files $uri index.html =404;
}
```

I also needed to have `<base href=<baseref> /> `in the head of index above any links.

All resource urls in head need to have the baseref added.  
Urls in the html should be relative to ``<baseref>`` i.e.

```
<li><a href="queue">Queue</a></li>
```
results in a url of `http://server/baseref/queue`
