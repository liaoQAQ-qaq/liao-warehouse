#!/bin/bash
# Git Workflow Helper Script
# 团队Git工作流自动化脚本

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
Git Workflow Helper Script

用法: $0 <command> [options]

命令:
    setup           配置Git工作流环境
    create-feature  创建功能分支
    create-bugfix   创建Bug修复分支
    create-hotfix   创建紧急修复分支
    check           检查Git工作流规范
    status          显示Git状态摘要
    clean           清理Git分支和标签
    sync            同步远程仓库
    pre-commit     执行提交前检查
    pre-push        执行推送前检查
    merge-branch    合并分支到main
    release         创建发布标签

选项:
    --branch <name>     指定分支名称
    --type <type>       指定提交类型
    --message <msg>     指定提交信息
    --force             强制执行操作
    --dry-run           模拟执行，不实际操作

示例:
    $0 setup                           # 配置Git工作流
    $0 create-feature user-auth        # 创建功能分支
    $0 check                           # 检查工作流规范
    $0 pre-commit                     # 执行提交前检查
    $0 merge-branch feature/login     # 合并功能分支

更多信息请参考：GIT_WORKFLOW.md
EOF
}

# 检查Git仓库
check_git_repo() {
    if [ ! -d .git ]; then
        log_error "当前目录不是Git仓库"
        exit 1
    fi
}

# 检查分支名称
check_branch_name() {
    local branch_name="$1"

    # 检查分支命名规范
    if [[ "$branch_name" =~ ^(feature|bugfix|hotfix|release)/.+$ ]]; then
        return 0
    else
        log_error "分支名称不符合规范，应该使用以下格式之一："
        log_error "  feature/<功能描述>"
        log_error "  bugfix/<问题描述>"
        log_error "  hotfix/<紧急修复>"
        log_error "  release/<版本号>"
        return 1
    fi
}

# 检查提交信息
check_commit_message() {
    local message="$1"

    # 检查提交信息格式
    if [[ "$message" =~ ^(feat|fix|docs|style|refactor|test|chore|perf|ci|build)(\(.+\))?: .+$ ]]; then
        return 0
    else
        log_error "提交信息格式不符合规范，应该使用以下格式："
        log_error "  <type>(<scope>): <subject>"
        log_error "  例如: feat(auth): add user login functionality"
        return 1
    fi
}

# 创建功能分支
create_feature_branch() {
    local feature_name="$1"
    local branch_name="feature/${feature_name}"

    log_info "创建功能分支: $branch_name"

    # 更新main分支
    log_info "更新main分支..."
    git fetch origin
    git checkout main
    git pull origin main

    # 创建功能分支
    git checkout -b "$branch_name"

    log_success "功能分支创建成功: $branch_name"
    log_info "现在可以开始开发功能了"
    log_info "开发完成后，使用以下命令提交PR:"
    log_info "  make check           # 检查代码质量"
    log_info "  git add .            # 添加文件"
    log_info "  git commit -m 'feat: 添加功能描述'  # 提交"
    log_info "  git push origin $branch_name  # 推送"
}

# 创建Bug修复分支
create_bugfix_branch() {
    local bug_description="$1"
    local branch_name="bugfix/${bug_description}"

    log_info "创建Bug修复分支: $branch_name"

    # 更新main分支
    log_info "更新main分支..."
    git fetch origin
    git checkout main
    git pull origin main

    # 创建Bug修复分支
    git checkout -b "$branch_name"

    log_success "Bug修复分支创建成功: $branch_name"
    log_info "现在可以开始修复Bug了"
}

# 创建紧急修复分支
create_hotfix_branch() {
    local hotfix_description="$1"
    local branch_name="hotfix/${hotfix_description}"

    log_info "创建紧急修复分支: $branch_name"

    # 基于最新tag创建分支
    local latest_tag=$(git describe --tags --abbrev=0)
    if [ -z "$latest_tag" ]; then
        log_warning "没有找到tag，基于main分支创建"
        git checkout main
    else
        log_info "基于tag $latest_tag 创建分支"
        git checkout "$latest_tag"
    fi

    # 创建紧急修复分支
    git checkout -b "$branch_name"

    log_success "紧急修复分支创建成功: $branch_name"
    log_info "请尽快修复并发布"
}

# 同步远程仓库
sync_remote() {
    log_info "同步远程仓库..."

    # 获取远程更新
    git fetch origin

    # 检查当前分支
    local current_branch=$(git branch --show-current)

    # 同步当前分支
    log_info "同步分支: $current_branch"
    git pull origin "$current_branch"

    log_success "远程仓库同步完成"
}

# 合并分支到main
merge_to_main() {
    local source_branch="$1"

    log_info "合并分支 $source_branch 到 main"

    # 切换到main分支
    git checkout main
    git pull origin main

    # 合并源分支
    git merge "$source_branch"

    log_success "分支合并完成"
    log_info "可以推送到远程仓库: git push origin main"
}

# 创建发布标签
create_release() {
    local version="$1"
    local tag_name="v$version"

    log_info "创建发布标签: $tag_name"

    # 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        log_error "有未提交的更改，请先提交"
        exit 1
    fi

    # 创建标签
    git tag -a "$tag_name" -m "Release $tag_name

    # 推送标签
    git push origin "$tag_name"

    log_success "发布标签创建成功: $tag_name"
}

# 检查Git工作流规范
check_workflow() {
    log_info "检查Git工作流规范..."

    # 检查Git配置
    log_info "=== Git配置检查 ==="
    git config --list --local | grep -E "(user\.|branch\.|core\.)"

    # 检查分支状态
    log_info "=== 分支状态检查 ==="
    git branch -a

    # 检查提交信息
    log_info "=== 提交信息检查 ==="
    local recent_commits=$(git log --oneline -5)
    if [ -n "$recent_commits" ]; then
        echo "$recent_commits"

        # 检查最近提交的格式
        local latest_commit=$(git log -1 --pretty=%B)
        if ! check_commit_message "$latest_commit"; then
            log_warning "最近的提交信息格式可能不符合规范"
        fi
    fi

    # 检查工作流文件
    log_info "=== 工作流文件检查 ==="
    local workflow_files=(
        ".github/workflows/claude.yml"
        ".github/workflows/claude-code-review.yml"
        "CONTRIBUTING.md"
        "GIT_WORKFLOW.md"
        ".github/pull_request_template.md"
    )

    for file in "${workflow_files[@]}"; do
        if [ -f "../$file" ]; then
            log_success "✓ $file"
        else
            log_warning "✗ $file (缺失)"
        fi
    done
}

# 清理Git分支和标签
cleanup_git() {
    log_info "清理Git环境..."

    # 清理已合并的本地分支
    log_info "清理已合并的本地分支..."
    local merged_branches=$(git branch --merged | grep -v "main\|develop\|master" | sed 's/^[* ]*//')
    for branch in $merged_branches; do
        if [ -n "$branch" ]; then
            log_info "删除分支: $branch"
            git branch -d "$branch" 2>/dev/null || git branch -D "$branch"
        fi
    done

    # 清理远程分支引用
    log_info "清理远程分支引用..."
    git remote prune origin

    # 清理临时标签
    log_info "清理临时标签..."
    local temp_tags=$(git tag -l "temp-*" 2>/dev/null || true)
    for tag in $temp_tags; do
        if [ -n "$tag" ]; then
            log_info "删除标签: $tag"
            git tag -d "$tag"
        fi
    done

    log_success "Git清理完成"
}

# 显示Git状态摘要
show_status() {
    log_info "Git状态摘要..."

    # 当前分支
    log_info "=== 当前分支 ==="
    git branch --show-current

    # 工作目录状态
    log_info "=== 工作目录状态 ==="
    git status --porcelain

    # 最近提交
    log_info "=== 最近提交 ==="
    git log --oneline -3

    # 远程状态
    log_info "=== 远程状态 ==="
    git remote -v

    # 待处理文件
    local staged_files=$(git diff --cached --name-only)
    local modified_files=$(git diff --name-only)
    local untracked_files=$(git ls-files --others --exclude-standard)

    if [ -n "$staged_files" ] || [ -n "$modified_files" ] || [ -n "$untracked_files" ]; then
        log_info "=== 文件状态 ==="
        [ -n "$staged_files" ] && echo "已暂存: $(echo $staged_files | wc -w) 个文件"
        [ -n "$modified_files" ] && echo "已修改: $(echo $modified_files | wc -w) 个文件"
        [ -n "$untracked_files" ] && echo "未跟踪: $(echo $untracked_files | wc -w) 个文件"
    fi
}

# 执行提交前检查
run_pre_commit() {
    log_info "执行提交前检查..."

    # 检查工作目录状态
    if [ -z "$(git status --porcelain)" ]; then
        log_info "没有待提交的更改"
        exit 0
    fi

    # 运行代码质量检查
    log_info "运行代码质量检查..."
    if ! make check 2>/dev/null; then
        log_error "代码质量检查失败，请修复后再提交"
        exit 1
    fi

    # 检查提交信息格式
    log_info "检查提交信息格式..."
    if [ -f .git/COMMIT_EDITMSG ]; then
        local commit_msg=$(cat .git/COMMIT_EDITMSG)
        if ! check_commit_message "$commit_msg"; then
            log_error "提交信息格式不正确，请参考CONTRIBUTING.md"
            exit 1
        fi
    fi

    log_success "提交前检查通过，可以提交代码"
}

# 执行推送前检查
run_pre_push() {
    log_info "执行推送前检查..."

    # 检查分支状态
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
        log_error "不允许直接推送到主分支，请创建PR"
        exit 1
    fi

    # 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        log_error "有未提交的更改，请先提交"
        exit 1
    fi

    # 运行完整测试
    log_info "运行完整测试..."
    if ! make test 2>/dev/null; then
        log_error "测试失败，请修复后再推送"
        exit 1
    fi

    # 检查是否需要创建PR
    if ! git log "origin/$current_branch..$current_branch" | grep -q .; then
        log_warning "没有新的提交，可能需要创建PR"
    else
        log_info "有新的提交可以推送"
    fi

    log_success "推送前检查通过"
}

# 主函数
main() {
    local command="${1:-}"
    local option=""
    local value=""

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --branch)
                shift
                value="$1"
                ;;
            --type)
                shift
                option="$1"
                ;;
            --message)
                shift
                option="$1"
                ;;
            --force)
                option="$option --force"
                ;;
            --dry-run)
                option="$option --dry-run"
                ;;
            *)
                if [ -z "$command" ]; then
                    command="$1"
                else
                    value="$1"
                fi
                ;;
        esac
        shift
    done

    # 检查Git仓库
    if [ "$command" != "help" ] && [ "$command" != "setup" ]; then
        check_git_repo
    fi

    # 执行命令
    case "$command" in
        setup)
            log_info "配置Git工作流环境..."
            # 这里可以添加具体的配置逻辑
            ;;
        create-feature)
            if [ -z "$value" ]; then
                log_error "请指定功能名称: $0 create-feature <功能名称>"
                exit 1
            fi
            create_feature_branch "$value"
            ;;
        create-bugfix)
            if [ -z "$value" ]; then
                log_error "请指定Bug描述: $0 create-bugfix <Bug描述>"
                exit 1
            fi
            create_bugfix_branch "$value"
            ;;
        create-hotfix)
            if [ -z "$value" ]; then
                log_error "请指定紧急修复描述: $0 create-hotfix <紧急修复描述>"
                exit 1
            fi
            create_hotfix_branch "$value"
            ;;
        check)
            check_workflow
            ;;
        status)
            show_status
            ;;
        clean)
            cleanup_git
            ;;
        sync)
            sync_remote
            ;;
        pre-commit)
            run_pre_commit
            ;;
        pre-push)
            run_pre_push
            ;;
        merge-branch)
            if [ -z "$value" ]; then
                log_error "请指定源分支: $0 merge-branch <源分支>"
                exit 1
            fi
            merge_to_main "$value"
            ;;
        release)
            if [ -z "$value" ]; then
                log_error "请指定版本号: $0 release <版本号>"
                exit 1
            fi
            create_release "$value"
            ;;
        help|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"
