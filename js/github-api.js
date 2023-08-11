// Realiza una solicitud fetch a la API de GitHub para obtener los datos de los repositorios
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

    // Limpia el contenido previo de la lista de repositorios
    repoList.innerHTML = '';

    // Recorre los datos de los repositorios y crea elementos para mostrar la lista y la cantidad de commits
    data.forEach(repo => {
      const listItem = document.createElement('li');
      const repoName = repo.full_name.split('/')[1]; // Obtén el nombre del repositorio
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
  })
  .catch(error => {
    console.error(error);
    const contributionsElement = document.querySelector('.contributions');
    contributionsElement.innerHTML = `
      <h2>Contributions Overview</h2>
      <p>Error fetching contributions data</p>
    `;
  });
