"""
Git 仓库管理器 - 负责本地 Git 仓库操作
复用自 config-agent 项目
"""
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class CommitInfo:
    """提交信息"""
    hash: str
    time: str
    author: str
    message: str


@dataclass
class FileChange:
    """文件变更信息"""
    change_type: str  # A=新增, M=修改, D=删除, R=重命名
    file_path: str
    old_path: Optional[str] = None  # 重命名时的旧路径


class GitRepoManager:
    """本地 Git 仓库管理器"""
    
    def __init__(self, repo_path: str):
        """
        初始化 Git 仓库管理器
        
        Args:
            repo_path: Git 仓库路径
        """
        self.repo_path = Path(repo_path)
        self._validate_repo()
    
    def _validate_repo(self) -> None:
        """验证是否为有效的 Git 仓库"""
        if not self.repo_path.exists():
            raise ValueError(f"仓库路径不存在: {self.repo_path}")
        
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"不是有效的 Git 仓库: {self.repo_path}")
    
    def _run_git_command(self, *args: str) -> str:
        """
        运行 Git 命令
        
        Args:
            *args: Git 命令参数
            
        Returns:
            命令输出结果
        """
        cmd = ["git", "-C", str(self.repo_path)] + list(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Git 命令执行失败: {' '.join(cmd)}\n"
                f"错误信息: {e.stderr}"
            ) from e
    
    def get_current_branch(self) -> str:
        """获取当前分支名称"""
        return self._run_git_command("branch", "--show-current")
    
    def get_all_branches(self) -> List[str]:
        """获取所有分支列表"""
        output = self._run_git_command("branch", "-a")
        branches = []
        for line in output.split("\n"):
            line = line.strip()
            if line:
                branch = line.lstrip("* ").strip()
                branches.append(branch)
        return branches
    
    def get_commits(self, commit_range: str) -> List[CommitInfo]:
        """
        获取提交记录
        
        Args:
            commit_range: 提交范围，如 'main..HEAD'
            
        Returns:
            提交信息列表
        """
        format_str = "%H|%ai|%an|%s"
        output = self._run_git_command("log", f"--format={format_str}", commit_range)
        
        commits = []
        if not output:
            return commits
        
        for line in output.split("\n"):
            if not line.strip():
                continue
            
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append(CommitInfo(
                    hash=parts[0],
                    time=parts[1],
                    author=parts[2],
                    message=parts[3]
                ))
        
        return commits
    
    def get_changed_files(
        self,
        commit_range: str,
        target_dir: Optional[str] = None
    ) -> List[FileChange]:
        """
        获取变更文件列表
        
        Args:
            commit_range: 提交范围
            target_dir: 目标目录（可选）
            
        Returns:
            文件变更列表
        """
        cmd_args = ["diff", "--name-status", commit_range]
        
        if target_dir:
            cmd_args.extend(["--", target_dir])
        
        output = self._run_git_command(*cmd_args)
        
        changes = []
        if not output:
            return changes
        
        for line in output.split("\n"):
            if not line.strip():
                continue
            
            parts = line.split("\t", 2)
            if len(parts) >= 2:
                change_type = parts[0][0]
                file_path = parts[1]
                
                old_path = None
                if change_type == 'R' and len(parts) == 3:
                    old_path = file_path
                    file_path = parts[2]
                
                changes.append(FileChange(
                    change_type=change_type,
                    file_path=file_path,
                    old_path=old_path
                ))
        
        return changes
    
    def get_file_diff(
        self,
        commit_range: str,
        file_path: str
    ) -> str:
        """
        获取文件的详细变更内容
        
        Args:
            commit_range: 提交范围
            file_path: 文件路径
            
        Returns:
            diff 内容
        """
        return self._run_git_command("diff", commit_range, "--", file_path)
    
    def get_commit_files(self, commit_hash: str) -> List[FileChange]:
        """
        获取单个提交涉及的文件
        
        Args:
            commit_hash: 提交哈希
            
        Returns:
            文件变更列表
        """
        output = self._run_git_command(
            "show",
            "--name-status",
            "--format=",
            commit_hash
        )
        
        changes = []
        if not output:
            return changes
        
        for line in output.split("\n"):
            if not line.strip():
                continue
            
            parts = line.split("\t", 2)
            if len(parts) >= 2:
                change_type = parts[0][0]
                file_path = parts[1]
                
                old_path = None
                if change_type == 'R' and len(parts) == 3:
                    old_path = file_path
                    file_path = parts[2]
                
                changes.append(FileChange(
                    change_type=change_type,
                    file_path=file_path,
                    old_path=old_path
                ))
        
        return changes
