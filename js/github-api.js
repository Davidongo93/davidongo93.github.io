fetch('https://api.github.com/users/davidongo93/repos')
  .then(response => response.json())
  .then(data => {
    const contributions = data.reduce((acc, repo) => {
      return acc + repo.stargazers_count + repo.forks_count + repo.watchers_count;
    }, 0);
    const repositoriesCount = data.length;
    const starsCount = data.reduce((acc, repo) => acc + repo.stargazers_count, 0);
    const forksCount = data.reduce((acc, repo) => acc + repo.forks_count, 0);

    document.getElementById('contributionsCount').textContent = contributions.toLocaleString();
    document.getElementById('repositoriesCount').textContent = repositoriesCount.toLocaleString();
    document.getElementById('starsCount').textContent = starsCount.toLocaleString();
    document.getElementById('forksCount').textContent = forksCount.toLocaleString();

    const repoList = document.getElementById('repoList');

    repoList.innerHTML = '';

    data.forEach(repo => {
      const listItem = document.createElement('li');
      const repoName = repo.full_name.split('/')[1];
      listItem.textContent = `${repoName}`;

      const commitsElement = document.createElement('span');
      commitsElement.className = 'commits-count';
      fetch(repo.commits_url.replace('{/sha}', ''))
        .then(response => response.json())
        .then(commits => {
          commitsElement.textContent = `\tCommits: ${commits.length}`;
        })
        .catch(error => {
          console.error(error);
          commitsElement.textContent = '\tCommits: Error fetching data';
        });

      listItem.appendChild(commitsElement);
      repoList.appendChild(listItem);
    });

    // Nueva solicitud fetch para obtener información del usuario
    fetch('https://api.github.com/users/davidongo93')
      .then(response => response.json())
      .then(userData => {
        const userInfo = document.getElementById('userInfo');
        userInfo.textContent = `Username: ${userData.login}, Name: ${userData.name}, Location: ${userData.location}`;
      })
      .catch(error => {
        console.error(error);
        const userInfo = document.getElementById('userInfo');
        userInfo.textContent = 'User information not available';
      });
  })
  .catch(error => {
    console.error(error);
    const contributionsElement = document.querySelector('.contributions');
    contributionsElement.innerHTML = `
      <h2>Contributions Overview</h2>
      <p>Error fetching contributions data</p>
    `;
  });
