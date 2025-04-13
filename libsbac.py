import sys
import argparse
from src.classes.sbac import SBAC

def main():
    sbac = SBAC()
    parser = argparse.ArgumentParser(description="SBAC - Simple Backup and Control")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new SBAC repository")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add file(s) to staging area")
    add_parser.add_argument("files", nargs="+", help="Files to add")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show the working tree status")

    # Commit command
    commit_parser = subparsers.add_parser("commit", help="Record changes to the repository")
    commit_parser.add_argument("-m", "--message", required=True, help="Commit message")

    # Log command
    log_parser = subparsers.add_parser("log", help="Show commit logs")

    # Checkout command
    checkout_parser = subparsers.add_parser("checkout", help="Switch branches or restore working tree files")
    checkout_parser.add_argument("target", help="Branch, commit or tag to checkout")

    # Branch command
    branch_parser = subparsers.add_parser("branch", help="Create, list or delete branches")
    branch_group = branch_parser.add_mutually_exclusive_group(required=True)
    branch_group.add_argument("-c", "--create", metavar="BRANCH_NAME", help="Create a new branch")
    branch_group.add_argument("-d", "--delete", metavar="BRANCH_NAME", help="Delete a branch")
    branch_group.add_argument("-l", "--list", action="store_true", help="List all branches")
    branch_parser.add_argument("-s", "--start-point", help="Start the new branch at specific commit/tag/branch")

    # List branches command (alternativo, puedes usar branch -l en su lugar)
    list_branches_parser = subparsers.add_parser("list-branches", help="List all branches")

    # Tag command
    tag_parser = subparsers.add_parser("tag", help="Create a tag reference")
    tag_parser.add_argument("tag_name", help="Name of the tag")

    # List tags command
    list_tags_parser = subparsers.add_parser("list-tags", help="List all tags")

    # Diff commits command
    diff_parser = subparsers.add_parser("diff", help="Show changes between commits")
    diff_parser.add_argument("commit1", help="First commit hash")
    diff_parser.add_argument("commit2", help="Second commit hash")

    # Diff tags command
    diff_tags_parser = subparsers.add_parser("diff-tags", help="Show changes between tags")
    diff_tags_parser.add_argument("tag1", help="First tag name")
    diff_tags_parser.add_argument("tag2", help="Second tag name")

    args = parser.parse_args()

    try:
        if args.command == "init":
            sbac.init()
        elif args.command == "add":
            sbac.add(args.files)
        elif args.command == "status":
            sbac.status()
        elif args.command == "commit":
            sbac.commit(args.message)
        elif args.command == "log":
            sbac.log()
        elif args.command == "checkout":
            sbac.checkout(args.target)
        elif args.command == "branch":
            if args.create:
                sbac.create_branch(args.create, args.start_point)
            elif args.delete:
                sbac.delete_branch(args.delete)
            elif args.list:
                sbac.list_branches()
        elif args.command == "list-branches":
            sbac.list_branches()
        elif args.command == "tag":
            sbac.tag(args.tag_name)
        elif args.command == "list-tags":
            sbac.list_tags()
        elif args.command == "diff":
            sbac.diff_commits(args.commit1, args.commit2)
        elif args.command == "diff-tags":
            sbac.diff_tags(args.tag1, args.tag2)
    except Exception as e:
        print(f"error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()