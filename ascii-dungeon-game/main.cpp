#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <cstdlib>
#include <ctime>
#include <limits>
#include <cmath>
#include <algorithm>

using namespace std;

// Grid symbols
const char WALL = '#';
const char EMPTY = '.';
const char FRISK = 'F';
const char SANS = 'S';
const char SAVE_POINT = '*';
const char MONSTER = 'M';
const char DETERMINATION = 'D';
const char BONE = '|';
const char EXIT_DOOR = 'E';

// Game constants
const int GRID_WIDTH = 25;
const int GRID_HEIGHT = 18;
const int MAX_MONSTERS = 4;
const int MAX_DETERMINATION = 5;

struct Position {
    int x, y;

    bool operator==(const Position& other) const {
        return x == other.x && y == other.y;
    }

    bool operator!=(const Position& other) const {
        return !(*this == other);
    }
};

class Game {
private:
    vector<vector<char>> grid;
    Position frisk;
    Position sans;
    Position exitDoor;
    vector<Position> monsters;
    vector<Position> bones; // Sans's attacks
    int hp;
    int determination;
    int turnCount;
    int gold;
    int saveCount;
    bool gameRunning;
    bool gameWon;
    bool sansActive;
    int sansMoveCooldown;
    int sansAttackCooldown;

public:
    Game() : hp(20), determination(0), turnCount(0), gold(0), saveCount(0),
             gameRunning(true), gameWon(false), sansActive(true),
             sansMoveCooldown(0), sansAttackCooldown(0) {
        srand(static_cast<unsigned int>(time(0)));
        initializeGrid();
        placeFrisk();
        placeSans();
        placeExitDoor();
        placeMonsters();
        placeDetermination();
        placeSavePoints();
        displayHelp(); // Display help at the start
    }

    void initializeGrid() {
        grid.resize(GRID_HEIGHT, vector<char>(GRID_WIDTH, EMPTY));

        // Create border walls
        for (int i = 0; i < GRID_HEIGHT; i++) {
            grid[i][0] = WALL;
            grid[i][GRID_WIDTH - 1] = WALL;
        }
        for (int j = 0; j < GRID_WIDTH; j++) {
            grid[0][j] = WALL;
            grid[GRID_HEIGHT - 1][j] = WALL;
        }

        // Create some room-like structures (Undertale style)
        createRooms();
    }

    void createRooms() {
        // Horizontal walls to create rooms
        for (int j = 5; j < 20; j++) {
            if (j != 12) grid[6][j] = WALL;
        }

        for (int j = 3; j < 15; j++) {
            if (j != 9) grid[12][j] = WALL;
        }

        // Vertical walls
        for (int i = 3; i < 10; i++) {
            if (i != 6) grid[i][15] = WALL;
        }

        // Add some scattered obstacles
        for (int i = 0; i < 12; i++) {
            int x = rand() % (GRID_WIDTH - 2) + 1;
            int y = rand() % (GRID_HEIGHT - 2) + 1;
            if (grid[y][x] == EMPTY) {
                grid[y][x] = WALL;
            }
        }
    }

    void placeFrisk() {
        frisk.x = 2;
        frisk.y = 2;
        grid[frisk.y][frisk.x] = FRISK;
    }

    void placeSans() {
        sans.x = GRID_WIDTH - 3;
        sans.y = GRID_HEIGHT - 3;
        grid[sans.y][sans.x] = SANS;
    }

    void placeExitDoor() {
        exitDoor.x = GRID_WIDTH - 2;
        exitDoor.y = 1;
        grid[exitDoor.y][exitDoor.x] = EXIT_DOOR;
    }

    void placeMonsters() {
        for (int i = 0; i < MAX_MONSTERS; i++) {
            Position pos = getRandomEmptyPosition();
            monsters.push_back(pos);
            grid[pos.y][pos.x] = MONSTER;
        }
    }

    void placeDetermination() {
        for (int i = 0; i < MAX_DETERMINATION; i++) {
            Position pos = getRandomEmptyPosition();
            grid[pos.y][pos.x] = DETERMINATION;
        }
    }

    void placeSavePoints() {
        for (int i = 0; i < 3; i++) {
            Position pos = getRandomEmptyPosition();
            grid[pos.y][pos.x] = SAVE_POINT;
        }
    }

    Position getRandomEmptyPosition() {
        int x, y;
        do {
            x = rand() % (GRID_WIDTH - 2) + 1;
            y = rand() % (GRID_HEIGHT - 2) + 1;
        } while (grid[y][x] != EMPTY);
        return {x, y};
    }

    void displayGrid() {
        system("clear"); // Clear screen for UNIX systems

        cout << "\n╔═══════════════════════════════════════════════════════════════════╗\n";
        cout << "║              ❤ UNDERTALE - TEXT ADVENTURE ❤                      ║\n";
        cout << "║                    * Stay Determined *                            ║\n";
        cout << "╚═══════════════════════════════════════════════════════════════════╝\n\n";

        for (int i = 0; i < GRID_HEIGHT; i++) {
            cout << "  ";
            for (int j = 0; j < GRID_WIDTH; j++) {
                cout << grid[i][j] << " ";
            }
            cout << "\n";
        }
        cout << "\n";
    }

    void displayStatus() {
        cout << "┌───────────────────────────────────────────────────────────────────┐\n";
        cout << "│ ❤ HP: " << hp << "/20"
             << " | ⚡ DETERMINATION: " << determination
             << " | 💰 GOLD: " << gold
             << " | 🕐 TURN: " << turnCount << " │\n";
        cout << "└───────────────────────────────────────────────────────────────────┘\n";

        if (sansActive) {
            int distance = abs(frisk.x - sans.x) + abs(frisk.y - sans.y);
            if (distance < 8) {
                cout << "\n💀 Sans: \"you're gonna have a bad time...\"\n";
            }
        }
    }

    void displayHelp() {
        cout << "\n╔═══════════════════════════════════════════════════════════════════╗\n";
        cout << "║                         ❤ HELP MENU ❤                            ║\n";
        cout << "╠═══════════════════════════════════════════════════════════════════╣\n";
        cout << "║ CONTROLS:                                                         ║\n";
        cout << "║   W or w - Move UP                                                ║\n";
        cout << "║   S or s - Move DOWN                                              ║\n";
        cout << "║   A or a - Move LEFT                                              ║\n";
        cout << "║   D or d - Move RIGHT                                             ║\n";
        cout << "║   H or h - Display this help menu                                 ║\n";
        cout << "║   Q or q - Quit game                                              ║\n";
        cout << "╠═══════════════════════════════════════════════════════════════════╣\n";
        cout << "║ SYMBOLS:                                                          ║\n";
        cout << "║   F - Frisk (You, the human child)                                ║\n";
        cout << "║   S - Sans (Intelligent enemy)                                    ║\n";
        cout << "║   # - Wall (impassable)                                           ║\n";
        cout << "║   . - Empty tile                                                  ║\n";
        cout << "║   M - Monster (costs 3 HP, gives 10 gold if you have DETERMINATION)║\n";
        cout << "║   | - Bone (Sans's attack, costs 5 HP)                            ║\n";
        cout << "║   D - Determination (collect to spare monsters & gain power)      ║\n";
        cout << "║   * - Save Point (restore HP to full)                             ║\n";
        cout << "║   E - Exit Door (reach to escape the Underground!)                ║\n";
        cout << "╠═══════════════════════════════════════════════════════════════════╣\n";
        cout << "║ STORY:                                                            ║\n";
        cout << "║   You are Frisk, trapped in the Underground. Sans is hunting      ║\n";
        cout << "║   you down using his skeleton magic. Collect DETERMINATION to     ║\n";
        cout << "║   gain the power to spare monsters. Reach the EXIT to win!        ║\n";
        cout << "║                                                                   ║\n";
        cout << "║   * Stay Determined! *                                            ║\n";
        cout << "╚═══════════════════════════════════════════════════════════════════╝\n\n";
    }

    // BFS Pathfinding for Sans
    vector<Position> bfsPathfind(Position start, Position target) {
        if (start == target) return {};

        queue<Position> q;
        vector<vector<bool>> visited(GRID_HEIGHT, vector<bool>(GRID_WIDTH, false));
        vector<vector<Position>> parent(GRID_HEIGHT, vector<Position>(GRID_WIDTH, {-1, -1}));

        q.push(start);
        visited[start.y][start.x] = true;

        int dx[] = {0, 0, 1, -1};
        int dy[] = {1, -1, 0, 0};

        bool found = false;

        while (!q.empty() && !found) {
            Position current = q.front();
            q.pop();

            for (int i = 0; i < 4; i++) {
                int newX = current.x + dx[i];
                int newY = current.y + dy[i];

                if (newX < 0 || newX >= GRID_WIDTH || newY < 0 || newY >= GRID_HEIGHT)
                    continue;

                if (visited[newY][newX])
                    continue;

                char tile = grid[newY][newX];
                if (tile == WALL || tile == MONSTER || tile == BONE)
                    continue;

                visited[newY][newX] = true;
                parent[newY][newX] = current;
                q.push({newX, newY});

                if (newX == target.x && newY == target.y) {
                    found = true;
                    break;
                }
            }
        }

        if (!found) return {};

        // Reconstruct path
        vector<Position> path;
        Position current = target;

        while (!(current.x == start.x && current.y == start.y)) {
            path.push_back(current);
            current = parent[current.y][current.x];
            if (current.x == -1) break;
        }

        reverse(path.begin(), path.end());
        return path;
    }

    void moveSans() {
        if (!sansActive) return;

        if (sansMoveCooldown > 0) {
            sansMoveCooldown--;
            return;
        }

        // Use BFS to find path to Frisk
        vector<Position> path = bfsPathfind(sans, frisk);

        if (!path.empty() && path.size() > 1) {
            // Clear old position
            grid[sans.y][sans.x] = EMPTY;

            // Move to next position in path
            sans = path[0];

            // Check if Sans caught Frisk
            if (sans == frisk) {
                hp -= 10;
                cout << "\n💀 Sans caught you! \"geeettttttt dunked on!!!\" -10 HP\n";
                // Push Frisk back
                frisk.x = max(1, frisk.x - 1);
                frisk.y = max(1, frisk.y - 1);
            } else {
                grid[sans.y][sans.x] = SANS;
            }

            sansMoveCooldown = 1; // Sans moves every other turn
        }
    }

    void sansAttack() {
        if (!sansActive) return;

        if (sansAttackCooldown > 0) {
            sansAttackCooldown--;
            return;
        }

        int distance = abs(frisk.x - sans.x) + abs(frisk.y - sans.y);

        if (distance < 6 && rand() % 100 < 40) { // 40% chance to attack if close
            // Spawn bone attack near Frisk
            int dx = (frisk.x > sans.x) ? 1 : -1;
            int dy = (frisk.y > sans.y) ? 1 : -1;

            Position bonePos = {sans.x + dx, sans.y + dy};

            if (bonePos.x > 0 && bonePos.x < GRID_WIDTH - 1 &&
                bonePos.y > 0 && bonePos.y < GRID_HEIGHT - 1) {

                if (grid[bonePos.y][bonePos.x] == EMPTY) {
                    bones.push_back(bonePos);
                    grid[bonePos.y][bonePos.x] = BONE;
                    cout << "\n💀 Sans attacks! A bone appears!\n";
                }
            }

            sansAttackCooldown = 3;
        }
    }

    void updateBones() {
        // Move bones toward Frisk
        for (auto it = bones.begin(); it != bones.end(); ) {
            grid[it->y][it->x] = EMPTY;

            // Move bone toward Frisk
            if (it->x < frisk.x) it->x++;
            else if (it->x > frisk.x) it->x--;

            if (it->y < frisk.y) it->y++;
            else if (it->y > frisk.y) it->y--;

            // Check collision with Frisk
            if (it->x == frisk.x && it->y == frisk.y) {
                hp -= 5;
                cout << "\n💀 A bone hit you! -5 HP\n";
                it = bones.erase(it);
                continue;
            }

            // Check if bone hit wall
            if (grid[it->y][it->x] == WALL || it->x < 0 || it->x >= GRID_WIDTH || it->y < 0 || it->y >= GRID_HEIGHT) {
                it = bones.erase(it);
                continue;
            }

            grid[it->y][it->x] = BONE;
            ++it;
        }
    }

    bool isValidMove(int x, int y) {
        return (x >= 0 && x < GRID_WIDTH && y >= 0 && y < GRID_HEIGHT && grid[y][x] != WALL);
    }

    void moveFrisk(int dx, int dy) {
        int newX = frisk.x + dx;
        int newY = frisk.y + dy;

        if (!isValidMove(newX, newY)) {
            cout << "⚠ Cannot move there! (Wall or out of bounds)\n";
            return;
        }

        char targetTile = grid[newY][newX];

        // Clear old position
        grid[frisk.y][frisk.x] = EMPTY;

        // Update Frisk position
        frisk.x = newX;
        frisk.y = newY;

        // Handle tile interactions
        switch (targetTile) {
            case SANS:
                hp -= 10;
                cout << "💀 Sans: \"you're gonna have a bad time...\" -10 HP\n";
                break;
            case MONSTER:
                if (determination > 0) {
                    determination--;
                    gold += 10;
                    cout << "❤ You SPARED the monster! +10 Gold\n";
                    removeMonster(newX, newY);
                } else {
                    hp -= 3;
                    cout << "⚔ Monster attacked you! -3 HP (Need DETERMINATION to spare)\n";
                    removeMonster(newX, newY);
                }
                break;
            case BONE:
                hp -= 5;
                cout << "💀 You touched a bone attack! -5 HP\n";
                removeBone(newX, newY);
                break;
            case DETERMINATION:
                determination++;
                cout << "❤ * You are filled with DETERMINATION. *\n";
                break;
            case SAVE_POINT:
                hp = 20;
                saveCount++;
                cout << "❤ * File saved. HP restored! *\n";
                break;
            case EXIT_DOOR:
                gameWon = true;
                gameRunning = false;
                cout << "🎉 * You escaped the Underground! *\n";
                break;
        }

        // Place Frisk on new position
        grid[frisk.y][frisk.x] = FRISK;

        turnCount++;

        // Sans AI turn
        moveSans();
        sansAttack();
        updateBones();

        // Check if Frisk died
        if (hp <= 0) {
            gameRunning = false;
            cout << "\n💀 * You cannot give up just yet... *\n";
            cout << "💀 * But it refused. *\n";
            cout << "GAME OVER\n";
        }
    }

    void removeMonster(int x, int y) {
        monsters.erase(remove_if(monsters.begin(), monsters.end(),
                                   [x, y](const Position& m) { return m.x == x && m.y == y; }),
                        monsters.end());
    }

    void removeBone(int x, int y) {
        bones.erase(remove_if(bones.begin(), bones.end(),
                               [x, y](const Position& b) { return b.x == x && b.y == y; }),
                     bones.end());
    }

    void processInput() {
        cout << "\nEnter command (WASD to move, H for help, Q to quit): ";
        string input;
        cin >> input;

        if (input.empty()) return;

        char command = tolower(input[0]);

        switch (command) {
            case 'w':
                moveFrisk(0, -1);
                break;
            case 's':
                moveFrisk(0, 1);
                break;
            case 'a':
                moveFrisk(-1, 0);
                break;
            case 'd':
                moveFrisk(1, 0);
                break;
            case 'h':
                displayHelp();
                cout << "Press Enter to continue...";
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                cin.get();
                break;
            case 'q':
                gameRunning = false;
                cout << "* Determination. *\n";
                break;
            default:
                cout << "⚠ Invalid command! Use WASD to move, H for help.\n";
                break;
        }
    }

    void displayEndScreen() {
        cout << "\n╔═══════════════════════════════════════════════════════════════════╗\n";
        if (gameWon) {
            cout << "║                    ❤ YOU WON! ❤                                  ║\n";
            cout << "║              * You escaped the Underground! *                     ║\n";
        } else if (hp <= 0) {
            cout << "║                    💀 GAME OVER 💀                                ║\n";
            cout << "║              * But it refused. *                                  ║\n";
        } else {
            cout << "║                    * GAME ENDED *                                 ║\n";
        }
        cout << "╠═══════════════════════════════════════════════════════════════════╣\n";
        cout << "║ FINAL STATS:                                                      ║\n";
        cout << "║   Turns Survived: " << turnCount << "                                           ║\n";
        cout << "║   Final HP: " << hp << "/20                                                 ║\n";
        cout << "║   Gold Collected: " << gold << "                                             ║\n";
        cout << "║   Times Saved: " << saveCount << "                                               ║\n";
        cout << "║   Determination: " << determination << "                                             ║\n";
        cout << "╠═══════════════════════════════════════════════════════════════════╣\n";
        if (gameWon) {
            cout << "║  Sans: \"welp, you made it. guess you really are determined.\"     ║\n";
        } else {
            cout << "║  Sans: \"don't worry, kid. you'll get 'em next time.\"             ║\n";
        }
        cout << "╚═══════════════════════════════════════════════════════════════════╝\n\n";
    }

    void run() {
        cout << "Press Enter to start your journey...";
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
        cin.get();

        while (gameRunning) {
            displayGrid();
            displayStatus();
            processInput();
        }

        displayGrid();
        displayEndScreen();
    }
};

int main() {
    cout << "❤══════════════════════════════════════════════════════════════════❤\n";
    cout << "                        UNDERTALE                                   \n";
    cout << "                   Text Adventure Game                              \n";
    cout << "                  * Stay Determined *                               \n";
    cout << "❤══════════════════════════════════════════════════════════════════❤\n\n";
    cout << "Loading game...\n\n";

    Game game;
    game.run();

    return 0;
}
