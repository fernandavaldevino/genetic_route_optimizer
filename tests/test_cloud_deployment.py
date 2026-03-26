"""
Testes para funcionalidades de Cloud (GCP, Cloud Build, Terraform)
Testa configurações de deployment e infraestrutura
"""

import pytest
import yaml
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestCloudBuildConfiguration:
    """ Testes para configuração do Cloud Build """
    
    def test_cloudbuild_yaml_exists(self):
        """ Testa se o arquivo cloudbuild.yaml existe """
        cloudbuild_path = Path("cloudbuild.yaml")
        assert cloudbuild_path.exists(), "cloudbuild.yaml não encontrado"
    
    def test_cloudbuild_yaml_valid_syntax(self):
        """ Testa se cloudbuild.yaml tem sintaxe YAML válida """
        cloudbuild_path = Path("cloudbuild.yaml")
        
        with open(cloudbuild_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_cloudbuild_has_required_steps(self):
        """ Testa se cloudbuild.yaml tem os passos necessários """
        cloudbuild_path = Path("cloudbuild.yaml")
        
        with open(cloudbuild_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert 'steps' in config
        assert len(config['steps']) > 0
        
        # Verificar se tem passo de build
        build_steps = [step for step in config['steps'] if 'build' in step.get('args', [])]
        assert len(build_steps) > 0, "Nenhum passo de build encontrado"
        
        # Verificar se tem passo de push
        push_steps = [step for step in config['steps'] if 'push' in step.get('args', [])]
        assert len(push_steps) > 0, "Nenhum passo de push encontrado"
    
    def test_cloudbuild_has_images_section(self):
        """ Testa se cloudbuild.yaml tem seção de imagens """
        cloudbuild_path = Path("cloudbuild.yaml")
        
        with open(cloudbuild_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert 'images' in config
        assert len(config['images']) > 0
    
    def test_cloudbuild_has_timeout(self):
        """ Testa se cloudbuild.yaml tem timeout configurado """
        cloudbuild_path = Path("cloudbuild.yaml")
        
        with open(cloudbuild_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert 'timeout' in config
        assert config['timeout'] is not None
    
    def test_cloudbuild_docker_image_tags(self):
        """ Testa se as imagens Docker têm tags apropriadas """
        cloudbuild_path = Path("cloudbuild.yaml")
        
        with open(cloudbuild_path, 'r') as f:
            config = yaml.safe_load(f)
        
        images = config.get('images', [])
        
        # Verificar se tem pelo menos uma imagem com tag 'latest'
        latest_images = [img for img in images if ':latest' in img]
        assert len(latest_images) > 0, "Nenhuma imagem com tag 'latest' encontrada"
        
        # Verificar se tem pelo menos uma imagem com versão
        versioned_images = [img for img in images if ':v' in img]
        assert len(versioned_images) > 0, "Nenhuma imagem versionada encontrada"


class TestTerraformConfiguration:
    """ Testes para configuração do Terraform """
    
    def test_terraform_directory_exists(self):
        """Testa se o diretório terraform existe"""
        terraform_dir = Path("terraform")
        assert terraform_dir.exists(), "Diretório terraform não encontrado"
        assert terraform_dir.is_dir(), "terraform não é um diretório"
    
    def test_terraform_main_file_exists(self):
        """T esta se o arquivo main.tf existe """
        main_tf = Path("terraform/main.tf")
        assert main_tf.exists(), "terraform/main.tf não encontrado"
    
    def test_terraform_variables_file_exists(self):
        """ Testa se o arquivo variables.tf existe """
        variables_tf = Path("terraform/variables.tf")
        assert variables_tf.exists(), "terraform/variables.tf não encontrado"
    
    def test_terraform_outputs_file_exists(self):
        """ Testa se o arquivo outputs.tf existe """
        outputs_tf = Path("terraform/outputs.tf")
        assert outputs_tf.exists(), "terraform/outputs.tf não encontrado"
    
    def test_terraform_provider_file_exists(self):
        """ Testa se o arquivo provider.tf existe """
        provider_tf = Path("terraform/provider.tf")
        assert provider_tf.exists(), "terraform/provider.tf não encontrado"
    
    def test_terraform_main_has_cloud_run_resource(self):
        """ Testa se main.tf define recurso Cloud Run """
        main_tf = Path("terraform/main.tf")
        
        with open(main_tf, 'r') as f:
            content = f.read()
        
        assert 'google_cloud_run' in content, "Recurso Cloud Run não encontrado"
        assert 'resource' in content, "Nenhum recurso definido"
    
    def test_terraform_main_has_iam_configuration(self):
        """ Testa se main.tf tem configuração de IAM """
        main_tf = Path("terraform/main.tf")
        
        with open(main_tf, 'r') as f:
            content = f.read()
        
        # Verificar se tem configuração de IAM para acesso público
        assert 'iam' in content.lower(), "Configuração IAM não encontrada"
    
    def test_terraform_cloud_run_has_required_settings(self):
        """ Testa se Cloud Run tem configurações necessárias """
        main_tf = Path("terraform/main.tf")
        
        with open(main_tf, 'r') as f:
            content = f.read()
        
        # Verificar configurações importantes
        assert 'container_port' in content or 'port' in content, "Porta do container não configurada"
        assert 'cpu' in content, "CPU não configurada"
        assert 'memory' in content, "Memória não configurada"
    
    def test_terraform_has_scaling_configuration(self):
        """ Testa se tem configuração de scaling """
        main_tf = Path("terraform/main.tf")
        
        with open(main_tf, 'r') as f:
            content = f.read()
        
        assert 'scaling' in content or 'min_instance' in content or 'max_instance' in content, \
            "Configuração de scaling não encontrada"


class TestDockerConfiguration:
    """ Testes para configuração do Docker """
    
    def test_dockerfile_exists(self):
        """ Testa se o Dockerfile existe """
        dockerfile = Path("Dockerfile")
        assert dockerfile.exists(), "Dockerfile não encontrado"
    
    def test_dockerfile_has_python_base_image(self):
        """ Testa se Dockerfile usa imagem base Python """
        dockerfile = Path("Dockerfile")
        
        with open(dockerfile, 'r') as f:
            content = f.read()
        
        assert 'FROM python' in content, "Imagem base Python não encontrada"
    
    def test_dockerfile_has_workdir(self):
        """ Testa se Dockerfile define WORKDIR """
        dockerfile = Path("Dockerfile")
        
        with open(dockerfile, 'r') as f:
            content = f.read()
        
        assert 'WORKDIR' in content, "WORKDIR não definido"
    
    def test_dockerfile_copies_requirements(self):
        """ Testa se Dockerfile copia requirements.txt ou instala dependências """
        dockerfile = Path("Dockerfile")
        
        with open(dockerfile, 'r') as f:
            content = f.read()
        
        # Aceitar tanto COPY requirements.txt quanto pip install direto
        has_requirements = 'requirements.txt' in content or 'pip install' in content
        assert has_requirements, "Dockerfile não copia requirements.txt nem instala dependências"
    
    def test_dockerfile_installs_dependencies(self):
        """ Testa se Dockerfile instala dependências """
        dockerfile = Path("Dockerfile")
        
        with open(dockerfile, 'r') as f:
            content = f.read()
        
        assert 'pip install' in content, "Instalação de dependências não encontrada"
    
    def test_dockerfile_exposes_port(self):
        """ Testa se Dockerfile expõe porta """
        dockerfile = Path("Dockerfile")
        
        with open(dockerfile, 'r') as f:
            content = f.read()
        
        assert 'EXPOSE' in content or '8080' in content, "Porta não exposta"
    
    def test_dockerfile_has_cmd_or_entrypoint(self):
        """ Testa se Dockerfile tem CMD ou ENTRYPOINT """
        dockerfile = Path("Dockerfile")
        
        with open(dockerfile, 'r') as f:
            content = f.read()
        
        assert 'CMD' in content or 'ENTRYPOINT' in content, \
            "CMD ou ENTRYPOINT não definido"


class TestEnvironmentConfiguration:
    """ Testes para configuração de ambiente """
    
    def test_env_example_has_required_variables(self):
        """ Testa se .env.example tem variáveis necessárias """
        env = Path(".env")
        
        with open(env, 'r') as f:
            content = f.read()
        
        # Verificar variáveis importantes (todas devem existir)
        required_vars = [
            'LLM_PROVIDER',
            'OPENAI_API_KEY',
            'OPENAI_MODEL',
            'OPENAI_TEMPERATURE',
            'OLLAMA_BASE_URL',
            'OLLAMA_MODEL',
            'OLLAMA_TEMPERATURE',
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_BOT_USERNAME',
            'BOT_NAME'
        ]
        
        missing_vars = [var for var in required_vars if var not in content]
        assert len(missing_vars) == 0, f"Variáveis faltando em .env: {', '.join(missing_vars)}"
    
    def test_gitignore_excludes_env_file(self):
        """ Testa se .gitignore exclui arquivo .env """
        gitignore = Path(".gitignore")
        
        if gitignore.exists():
            with open(gitignore, 'r') as f:
                content = f.read()
            
            assert '.env' in content, ".env não está no .gitignore"

    
class TestMakefile:
    """ Testes para Makefile """
    
    def test_makefile_exists(self):
        """ Testa se Makefile existe """
        makefile = Path("Makefile")
        assert makefile.exists(), "Makefile não encontrado"
    
    def test_makefile_has_common_targets(self):
        """ Testa se Makefile tem targets comuns """
        makefile = Path("Makefile")
        
        with open(makefile, 'r') as f:
            content = f.read()
        
        # Verificar targets comuns
        common_targets = ['test', 'run', 'install']
        
        found_targets = []
        for target in common_targets:
            if f'{target}:' in content:
                found_targets.append(target)
        
        assert len(found_targets) > 0, "Nenhum target comum encontrado no Makefile"


class TestCloudRunDeployment:
    """ Testes para deployment no Cloud Run """
    
    @patch.dict(os.environ, {'GCP_PROJECT_ID': 'test-project'})
    def test_environment_variables_for_deployment(self):
        """ Testa se variáveis de ambiente necessárias estão disponíveis """
        # Este teste verifica se as variáveis podem ser configuradas
        assert os.getenv('GCP_PROJECT_ID') == 'test-project'
    
    def test_api_port_configuration(self):
        """ Testa se a porta da API está configurada corretamente """
        # Verificar se a porta 8080 é usada (padrão Cloud Run)
        main_api = Path("api/main.py")
        
        if main_api.exists():
            with open(main_api, 'r') as f:
                content = f.read()
            
            assert '8080' in content, "Porta 8080 não configurada na API"
    
    def test_requirements_file_exists(self):
        """ Testa se requirements.txt existe """
        requirements = Path("requirements.txt")
        assert requirements.exists(), "requirements.txt não encontrado"
    
    def test_requirements_has_fastapi(self):
        """ Testa se requirements.txt inclui FastAPI """
        requirements = Path("requirements.txt")
        
        with open(requirements, 'r') as f:
            content = f.read()
        
        assert 'fastapi' in content.lower(), "FastAPI não está em requirements.txt"
    
    def test_requirements_has_uvicorn(self):
        """ Testa se requirements.txt inclui Uvicorn """
        requirements = Path("requirements.txt")
        
        with open(requirements, 'r') as f:
            content = f.read()
        
        assert 'uvicorn' in content.lower(), "Uvicorn não está em requirements.txt"


class TestCloudBuildIntegration:
    """ Testes de integração para Cloud Build """
    
    def test_cloudbuild_references_correct_dockerfile(self):
        """ Testa se cloudbuild.yaml referencia Dockerfile correto """
        cloudbuild_path = Path("cloudbuild.yaml")
        dockerfile_path = Path("Dockerfile")
        
        assert dockerfile_path.exists(), "Dockerfile não existe"
        
        with open(cloudbuild_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Verificar se algum step usa docker build
        build_steps = [step for step in config['steps'] if 'docker' in step.get('name', '')]
        assert len(build_steps) > 0, "Nenhum step Docker encontrado"
    
    def test_image_naming_consistency(self):
        """ Testa consistência de nomenclatura de imagens """
        cloudbuild_path = Path("cloudbuild.yaml")
        
        with open(cloudbuild_path, 'r') as f:
            config = yaml.safe_load(f)
        
        images = config.get('images', [])
        
        # Verificar se todas as imagens têm o mesmo repositório base
        if len(images) > 1:
            base_repos = set()
            for img in images:
                # Extrair repositório base (antes da tag)
                base_repo = img.split(':')[0] if ':' in img else img
                base_repos.add(base_repo)
            
            assert len(base_repos) == 1, "Imagens usam repositórios diferentes"
