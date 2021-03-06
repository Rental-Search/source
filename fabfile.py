from functools import wraps
from fabric.api import env, run, sudo, local, put, runs_once, cd, abort
from fabric.operations import _shell_escape
from fabric.state import output

def _run(command, shell=True, pty=True, combine_stderr=True, sudo=False, user=None):
    real_command = command
    if shell:
        # Handle cwd munging via 'cd' context manager
        cwd = env.get('cwd', '')
        if cwd:
            cwd = 'cd %s && ' % _shell_escape(cwd)
        # Construct final real, full command
        real_command = '%s "%s"' % (env.shell,
            _shell_escape(cwd + real_command))
        # Remove cwd from context
        env.cwd = ''
    if output.debug:
        print("[%s] run: %s" % (env.host_string, real_command))
    elif output.running:
        print("[%s] run: %s" % (env.host_string, command))
    local("ssh -A %s@%s '%s'" % (env.user, env.host_string, real_command))

def notify(func):
    """Notify campfire of a deploy"""
    @wraps(func)
    def decorated(*args, **kwargs):
        from pinder import Campfire
        if not 'campfire_domain' in env:
            return
        if not 'current_release' in env:
            releases()
        if 'git_branch' not in env:
            env.git_branch = "master"
        deployed = run("cd %(current_release)s; git rev-parse HEAD" % env)[:7]
        deploying = run("cd %(current_release)s; git fetch deploy; git rev-parse deploy/%(git_branch)s" % env)[:7]
        return_value = func(*args, **kwargs)
        c = Campfire(env.campfire_domain, env.campfire_token, ssl=True)
        room = c.find_room_by_name(env.campfire_room)
        compare_url = "%(repo_url)s/compare/%(deployed)s...%(deploying)s" % {'repo_url': env.github_url, 'deployed':deployed, 'deploying':deploying}
        room.speak("%s has deployed new code on %s : %s" % (env.user, env.name, compare_url))
        return return_value
    return decorated

def production():
    """Defines production environment"""
    env.name = "production"
    env.user = "benoitw"
    env.hosts = ['goat.e-loue.com',]
    env.base_dir = "/var/www"
    env.app_name = "eloue"
    env.domain_name = "e-loue.com"
    env.domain_path = "%(base_dir)s/%(domain_name)s" % {'base_dir': env.base_dir, 'domain_name': env.domain_name}
    env.current_path = "%(domain_path)s/current" % {'domain_path': env.domain_path}
    env.releases_path = "%(domain_path)s/releases" % {'domain_path': env.domain_path}
    env.shared_path = "%(domain_path)s/shared" % {'domain_path': env.domain_path}
    env.git_clone = "git@github.com:e-loue/eloue.git"
    env.env_file = "deploy/production.txt"
    env.campfire_room = "Chit chat"
    env.campfire_token = "b96565fb9b8f49f0e18a6a194d7ac97812e154d6"
    env.campfire_domain = "e-loue"
    env.github_url = "https://github.com/e-loue/eloue"

def beta():
    """Defines beta environment"""
    env.name = "beta"
    env.user = "benoitw"
    env.hosts = ['goat.e-loue.com',]
    env.base_dir = "/var/www"
    env.app_name = "eloue"
    env.domain_name = "beta.e-loue.com"
    env.domain_path = "%(base_dir)s/%(domain_name)s" % {'base_dir': env.base_dir, 'domain_name': env.domain_name}
    env.current_path = "%(domain_path)s/current" % {'domain_path': env.domain_path}
    env.releases_path = "%(domain_path)s/releases" % {'domain_path': env.domain_path}
    env.shared_path = "%(domain_path)s/shared" % {'domain_path': env.domain_path}
    env.git_clone = "git@github.com:e-loue/eloue.git"
    env.env_file = "deploy/production.txt"
    env.campfire_room = "Chit chat"
    env.campfire_token = "b96565fb9b8f49f0e18a6a194d7ac97812e154d6"
    env.campfire_domain = "e-loue"
    env.github_url = "https://github.com/e-loue/eloue"
    env.git_branch = "beta"

def staging():
    """Defines staging environment"""
    env.name = "staging"
    env.user = "benoitw"
    env.hosts = ['staging.e-loue.com',]
    env.base_dir = "/var/www"
    env.app_name = "eloue"
    env.domain_name = "e-loue.com"
    env.domain_path = "%(base_dir)s/%(domain_name)s" % {'base_dir': env.base_dir, 'domain_name': env.domain_name}
    env.current_path = "%(domain_path)s/current" % {'domain_path': env.domain_path}
    env.releases_path = "%(domain_path)s/releases" % {'domain_path': env.domain_path}
    env.shared_path = "%(domain_path)s/shared" % {'domain_path': env.domain_path}
    env.git_clone = "git@github.com:e-loue/eloue.git"
    env.env_file = "deploy/production.txt"
    env.campfire_room = "Chit chat"
    env.campfire_token = "b96565fb9b8f49f0e18a6a194d7ac97812e154d6"
    env.campfire_domain = "e-loue"
    env.github_url = "https://github.com/e-loue/eloue"

def monkeysandbox():
    """Defines sandbox environment"""
    env.name = "monkeysandbox"
    env.user = "benoitw"
    env.hosts = ['monkeysandbox',]
    env.base_dir = "/var/www"
    env.app_name = "eloue"
    env.domain_name = "e-loue.com"
    env.domain_path = "%(base_dir)s/%(domain_name)s" % {'base_dir': env.base_dir, 'domain_name': env.domain_name}
    env.current_path = "%(domain_path)s/current" % {'domain_path': env.domain_path}
    env.releases_path = "%(domain_path)s/releases" % {'domain_path': env.domain_path}
    env.shared_path = "%(domain_path)s/shared" % {'domain_path': env.domain_path}
    env.git_clone = "git@github.com:benoitw/eloue.git"
    env.env_file = "deploy/production.txt"
    env.campfire_room = "Chit chat"
    env.campfire_token = "b96565fb9b8f49f0e18a6a194d7ac97812e154d6"
    env.campfire_domain = "e-loue"
    env.github_url = "https://github.com/benoitw/eloue"

@runs_once
def releases():
    """List a releases made"""
    env.releases = sorted(run('ls -x %(releases_path)s' % {'releases_path': env.releases_path}).split())
    if len(env.releases) >= 1:
        env.current_revision = env.releases[-1]
        env.current_release = "%(releases_path)s/%(current_revision)s" % {'releases_path': env.releases_path, 'current_revision': env.current_revision}
    if len(env.releases) > 1:
        env.previous_revision = env.releases[-2]
        env.previous_release = "%(releases_path)s/%(previous_revision)s" % {'releases_path': env.releases_path, 'previous_revision': env.previous_revision}

def start():
    """Start the application servers"""
    sudo("/etc/init.d/apache2 start")

def restart():
    """Restarts your application"""
    sudo("/etc/init.d/apache2 reload")

def stop():
    """Stop the application servers"""
    sudo("/etc/init.d/apache2 stop")

def permissions():
    """Make the release group-writable"""
    sudo("chmod -R g+w %(domain_path)s" % {'domain_path': env.domain_path})
    sudo("chown -R www-data:www-data %(domain_path)s" % {'domain_path': env.domain_path})

def setup():
    """Prepares one or more servers for deployment"""
    sudo("mkdir -p %(domain_path)s/{releases,shared}" % {'domain_path': env.domain_path})
    sudo("mkdir -p %(shared_path)s/{system,log}" % {'shared_path': env.shared_path})
    permissions()

def checkout():
    """Checkout code to the remote servers"""
    from time import time
    env.current_release = "%(releases_path)s/%(time).0f" % {'releases_path':  env.releases_path, 'time':  time()}
    with cd(env.releases_path):
        _run("git clone -q -o deploy --depth 1 %(git_clone)s %(current_release)s" % {'git_clone':  env.git_clone, 'current_release':  env.current_release})
    with cd(env.current_release):
        if 'git_branch' in env:
            _run("git checkout -b branch deploy/%(git_branch)s" % {'git_branch': env.git_branch})

def update():
    """Copies your project and updates environment and symlink"""
    update_code()
    update_env()
    symlink()
    permissions()

def update_code():
    """Copies your project to the remote servers"""
    checkout()
    permissions()

def symlink():
    """Updates the symlink to the most recently deployed version"""
    if not env.has_key('current_release'):
        releases()
    run("ln -nfs %(current_release)s %(current_path)s" % {'current_release': env.current_release, 'current_path': env.current_path})
    run("ln -nfs %(shared_path)s/log %(current_release)s/log" % {'shared_path': env.shared_path, 'current_release': env.current_release})
    run("ln -nfs %(shared_path)s/pictures %(current_release)s/eloue/media/pictures" % {'shared_path': env.shared_path, 'current_release': env.current_release})
    run("ln -nfs %(shared_path)s/system/local.py %(current_release)s/%(app_name)s/local.py" % {'shared_path': env.shared_path, 'current_release': env.current_release, 'app_name': env.app_name})
    run("ln -nfs %(current_release)s/env/lib/python2.6/site-packages/django/contrib/admin/media %(current_release)s/%(app_name)s/media/admin" % {'current_release': env.current_release, 'app_name': env.app_name})

def update_env():
    """Update servers environment on the remote servers"""
    if not env.has_key('current_release'):
        releases()
    with cd(env.current_release):
        run("virtualenv -q --no-site-packages --unzip-setuptools env")
        run("env/bin/pip -q install -r %(env_file)s" % {'env_file': env.env_file})
    permissions()

def migrate():
    """Run the migrate task"""
    if not env.has_key('current_release'):
        releases()
    with cd(env.current_release):
        run("source env/bin/activate; python %(app_name)s/manage.py syncdb --migrate --noinput" % {'app_name': env.app_name})

def compress():
    """Run the synccompress tasj"""
    if not 'current_release' in env:
        releases()
    with cd(env.current_release):
        run("env/bin/python %(app_name)s/manage.py collectstatic" % {'app_name': env.app_name})

def cleanup():
    """Clean up old releases"""
    if not env.has_key('releases'):
        releases()
    if len(env.releases) > 3:
        directories = env.releases
        directories.reverse()
        del directories[:3]
        env.directories = ' '.join([ "%(releases_path)s/%(release)s" % {'releases_path': env.releases_path, 'release': release} for release in directories ])
        run("rm -rf %(directories)s" % {'directories': env.directories})

def enable():
    """Makes the application web-accessible again"""
    run("rm %(shared_path)s/system/maintenance.html" % {'shared_path': env.shared_path})

def disable(**kwargs):
    """Present a maintenance page to visitors"""
    import os, datetime
    from django.conf import settings
    try:
        settings.configure(
            DEBUG=False, TEMPLATE_DEBUG=False, 
            TEMPLATE_DIRS=(os.path.join(os.getcwd(), 'eloue/templates/'),)
        )
    except EnvironmentError:
        pass
    from django.template.loader import render_to_string
    env.deadline = kwargs.get('deadline', None)
    env.reason = kwargs.get('reason', None)
    open("maintenance.html", "w").write(
        render_to_string("maintenance.html", {'now': datetime.datetime.now(), 'deadline': env.deadline, 'reason': env.reason}).encode('utf-8')
    )
    put('maintenance.html', '%(shared_path)s/system/maintenance.html' % {'shared_path': env.shared_path})
    local("rm maintenance.html")

def rollback_code():
    """Rolls back to the previously deployed version"""
    if not env.has_key('releases'):
        releases()
    if len(env.releases) >= 2:
        env.current_release = env.releases[-1]
        env.previous_revision = env.releases[-2]
        env.current_release = "%(releases_path)s/%(current_revision)s" % {'releases_path': env.releases_path, 'current_revision': env.current_revision}
        env.previous_release = "%(releases_path)s/%(previous_revision)s" % {'releases_path': env.releases_path, 'previous_revision': env.previous_revision}
        run("rm %(current_path)s; ln -s %(previous_release)s %(current_path)s && rm -rf %(current_release)s" % {'current_release': env.current_release, 'previous_release': env.previous_release, 'current_path': env.current_path})

def rollback():
    """Rolls back to a previous version and restarts"""
    rollback_code()
    restart()

def cold():
    """Deploys and starts a `cold' application"""
    update()
    migrate()
    compress()
    start()


def deploy():
    """Deploys your project. This calls both `update' and `restart'"""
    update()
    migrate()
    compress()
    restart()


def soft():
    """Deploys your project without updating the environnement"""
    if not env.has_key('current_release'):
        releases()
    with cd(env.current_release):
        if 'git_branch' not in env:
            env.git_branch = "master"
        _run("git pull -q deploy %(git_branch)s" % {'git_branch': env.git_branch})
    permissions()
    migrate()
    compress()
    restart()

def diff():
    """Show diff between current and deployed code"""
    if not 'current_release' in env:
        releases()
    if 'git_branch' not in env:
        env.git_branch = "master"
    deployed = run("cd %(current_release)s; git rev-parse HEAD" % env)[:7]
    deploying = run("cd %(current_release)s; git fetch deploy; git rev-parse deploy/%(git_branch)s" % env)[:7]
    local("git difftool %(deployed)s...%(deploying)s" % {'deployed':deployed, 'deploying':deploying})
