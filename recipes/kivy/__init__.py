from toolchain import CythonRecipe, shprint
from os.path import join
import sh


class KivyRecipe(CythonRecipe):
    version = "master"
    url = "https://github.com/kivy/kivy/archive/{version}.zip"
    library = "libkivy.a"
    depends = ["python", "sdl2", "sdl2_image", "sdl2_mixer", "sdl2_ttf", "ios"]
    pbx_frameworks = ["OpenGLES", "Accelerate", "AVFoundation", "CoreVideo",
                      "CoreMedia"]
    pre_build_ext = True

    def get_recipe_env(self, arch):
        env = super(KivyRecipe, self).get_recipe_env(arch)
        env["KIVY_SDL2_PATH"] = ":".join([
            join(self.ctx.dist_dir, "include", "common", "sdl2"),
            join(self.ctx.dist_dir, "include", "common", "sdl2_image"),
            join(self.ctx.dist_dir, "include", "common", "sdl2_ttf"),
            join(self.ctx.dist_dir, "include", "common", "sdl2_mixer")])
        return env

    def build_arch(self, arch):
        self._patch_setup()

        # this can be removed after the release of kivy version > 1.9.1
        self._patch_avfoundation()

        super(KivyRecipe, self).build_arch(arch)

    def _patch_setup(self):
        # patch setup to remove some functionnalities
        pyconfig = join(self.build_dir, "setup.py")
        def _remove_line(lines, pattern):
            for line in lines[:]:
                if pattern in line:
                    lines.remove(line)
        with open(pyconfig) as fd:
            lines = fd.readlines()
        _remove_line(lines, "flags['libraries'] = ['GLESv2']")
        #_remove_line(lines, "c_options['use_sdl'] = True")
        with open(pyconfig, "wb") as fd:
            fd.writelines(lines)

    def _patch_avfoundation(self):
        pyconfig = join(self.build_dir, "setup.py")
        shprint(
            sh.sed, "-i.bak",
            "s/c_options\['use_avfoundation'\] = platform == 'darwin'"
            "/c_options\['use_avfoundation'\] = platform in \['darwin', 'ios'\]/g",
            pyconfig)

        camera = join(self.build_dir, "kivy/core/camera/__init__.py")
        shprint(
            sh.sed, "-i.bak",
            "s/elif platform == 'macosx'/elif platform in \['macos', 'ios'\]/g",
            camera)


recipe = KivyRecipe()

