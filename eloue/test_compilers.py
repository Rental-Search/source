import pytest
from eloue.compat.pipeline.compilers import RequireJsCompiler
from pipeline.exceptions import CompilerError


@pytest.fixture
def buildjs(tmpdir):
    """
    Return a basic valid buildfile and its containing dir
    """
    buildfile = tmpdir.join("build.js")
    buildfile.write("""
({
    baseUrl: ".",
    paths: {
    },
    name: "main",
    out: "main-built.js"
})
""")
    return (tmpdir, buildfile)


class TestRequireJsCompiler():
    
    VALID_JS = "function what(a){return a;}"
    INVALID_JS = "function wha(a){"    
    
    def test_return_value_valid_input(self, buildjs):
        
        tmpdir, buildfile = buildjs
        
        infile = tmpdir.join("main.js")
        outfile = tmpdir.join("main-built.js")
        
        infile.write(self.VALID_JS)
             
        stdout = RequireJsCompiler(True, None).compile_file(buildfile.strpath, 
                                                   outfile.strpath)
        
        assert outfile.check()
    
    def test_return_value_invalid_input(self, buildjs):
        
        tmpdir, buildfile = buildjs
        
        infile = tmpdir.join("main.js")
        outfile = tmpdir.join("main-built.js")
        
        infile.write(self.INVALID_JS)
        
        with pytest.raises(CompilerError) as e:        
            stdout = RequireJsCompiler(True, None).compile_file(buildfile.strpath, 
                                                       outfile.strpath)
            
        assert not outfile.check()
        
        