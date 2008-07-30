try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='pySvnManager',
    version="0.1.3",
    description='SVN authz web management tools.',
    author='Jiang Xin',
    author_email='jiangxin@ossxp.com',
    url='https://sourceforge.net/projects/pysvnmanager',
    #install_requires=["Pylons>=0.9.6.2", "python-ldap"],
    install_requires=["Pylons>=0.9.6.2"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'pysvnmanager': ['i18n/*/LC_MESSAGES/*.mo', 'config/*.in']},
    message_extractors = {'pysvnmanager': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('public/**', 'ignore', None)]},
    entry_points="""
    [paste.app_factory]
    main = pysvnmanager.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
    zip_safe = False,
)
