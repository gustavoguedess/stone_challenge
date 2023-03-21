#include<stdio.h>
#include<string>
#include<time.h>

#define VERTICALMAX 100
#define HORIZONTALMAX 100
#define MAXSTAGES 500

int n = 65;
int m = 85;
int limit = MAXSTAGES;
int lab[MAXSTAGES][VERTICALMAX][HORIZONTALMAX];
int tries;

using namespace std;

void generate_mazes(){
    for(int s=0; s<MAXSTAGES-1; s++){
        printf("Gen stage %d\n", s);
        for(int i=0; i<n; i++){
            for(int j=0; j<m; j++){
                int adj = (i>0?lab[s][i-1][j]:0)+
                            (i<n-1?lab[s][i+1][j]:0)+
                            (j>0?lab[s][i][j-1]:0)+
                            (j<m-1?lab[s][i][j+1]:0)+
                            (i>0&&j>0?lab[s][i-1][j-1]:0)+
                            (i>0&&j<m-1?lab[s][i-1][j+1]:0)+
                            (i<n-1&&j>0?lab[s][i+1][j-1]:0)+
                            (i<n-1&&j<m-1?lab[s][i+1][j+1]:0);

                // White cells turn green if they have a number of adjacent green cells greater than 1 and less than 5. Otherwise, they remain white.
                if(!lab[s][i][j] && adj>1 && adj<5)
                    lab[s+1][i][j] = 1;
                else if(!lab[s][i][j])
                    lab[s+1][i][j] = 0;

                // Green cells remain green if they have a number of green adjacent cells greater than 3 and less than 6. Otherwise they become white.
                if(lab[s][i][j] && adj>3 && adj<6)
                    lab[s+1][i][j] = 1;
                else if(lab[s][i][j])
                    lab[s+1][i][j] = 0;
            }
        }
    }
}

void save_path(string path){
    FILE *f = fopen("path.txt", "w");
    for(int i=0; i<path.length(); i++){
        if(i!=0) fprintf(f, " ");
        fprintf(f, "%c", path[i]);
    }
    fclose(f);
}

void a_star(int x, int y, int c, string path){
    if(x<0 || y<0 || y>=n || x>=m || c>=limit)
        return;
    if(x==n-1 && y==m-1){
        printf("%d: %s\n", c, path.c_str());
        limit = c;
        save_path(path);
        return;
    }
    if(lab[c][y][x] || c+(n-y-1)+(m-x-1)>=limit || tries<=0){
        tries--;
        return;    
    }
    
    // printf("%3.d: (%.2d,%.2d), %s\n", c, x, y, path.c_str());
    int numbers[4] = {0, 1, 2, 3};
    if (rand() % 2 == 0)
        swap(numbers[0], numbers[1]);
    if (rand() % 2 == 0)
        swap(numbers[2], numbers[3]);

    for(int i=0; i<4; i++){
        switch(numbers[i]){
            case 0: a_star(x+1, y, c+1, path+"R"); break;
            case 1: a_star(x, y+1, c+1, path+"D"); break;
            case 2: a_star(x-1, y, c+1, path+"L"); break;
            case 3: a_star(x, y-1, c+1, path+"U"); break;
        }
    }
}

string load_path(){
    string path;
    FILE *f = fopen("path.txt", "r");
    printf("Load path\n");

    if(!f)
        return path;

    while(!feof(f)){
        char c;
        fscanf(f, "%c", &c);
        if(c=='R' || c=='D' || c=='L' || c=='U')
            path += c;
    }
    fclose(f);
    return path;
}

int main(){
    for(int i = 0; i<n; i++)
        for(int j = 0; j<m; j++){
            scanf("%d", &lab[0][i][j]);
            lab[0][i][j] = lab[0][i][j] == 1;
        }

    srand(time(NULL));

    string path = load_path();
    limit = path.length()==0?MAXSTAGES:path.length();
    
    generate_mazes();

    for(int s=0; s<300; s++){
        printf("Stage %d\n", s);
        for(int i=0; i<n; i++){
            for(int j=0; j<m; j++){
                printf("%d", lab[s][i][j]);
            }
            printf("\n");
        }
    }
    // while(1){
    //     printf("Gen new path\n");
    //     tries = 100000000;
    //     a_star(0, 0, 0, "");
    // }
}