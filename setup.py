from setuptools import setup

setup(
    name='usbguard-simple-gui-py-qt',
    version='0.0.1',

    author='Marco Nicola',
    author_email='marconicola@disroot.org',

    description='A simple unambitious system tray applet and GUI for '
                'interacting with USBGuard.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",

    keywords='usbguard',
    url='https://github.com/marco-nicola/usbguard-simple-gui-py-qt',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later '
            '(GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7'
    ],

    packages=['usbguard_simple_gui_py_qt'],
    entry_points={
        'gui_scripts': [
            ('usbguard-simple-gui-py-qt = ' 
                'usbguard_simple_gui_py_qt.system_tray_app:main'),
            ('usbguard-simple-gui-py-qt-window-only = ' 
                'usbguard_simple_gui_py_qt.main_window:main'),
        ]
    },
    package_data={
        '': ['*.svg']
    },
    python_requires='>=3.7.0,<3.8',
    install_requires=[
        'dbus-python>=1.2.12,<2',
        'PySide2>=5.13.2,<6',
    ]
)
